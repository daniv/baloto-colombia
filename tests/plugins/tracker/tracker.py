"""
PYTEST_DONT_REWRITE
"""

# — Project : baloto-colombia
# — File Name : plugin.py
# — Dir Path : tests/plugins/error_reporter
# — Created on: 2025–06–04 at 12:36:22.

from __future__ import annotations

import logging
import sys
import threading
import warnings
from functools import partialmethod
from pathlib import Path
from typing import Any
from typing import Literal
from typing import TYPE_CHECKING
from collections import Counter
from collections.abc import Callable
from collections.abc import Generator
from collections.abc import Mapping
from collections.abc import Sequence

import pendulum
import pytest
from rich.console import ConsoleRenderable
from rich.padding import Padding
from _pytest import timing

from baloto.cleo.io.outputs.output import Verbosity
from baloto.core.config.settings import settings
from baloto.core.rich.testers.messages import HookMessage
from helpers import cleanup_factory
from plugins.tracker.assert_report import AssertionReportException
from plugins.tracker.header import PytestEnvironment
from plugins.tracker.reporter import Reporter

if TYPE_CHECKING:
    from _pytest._code.code import ExceptionInfo
    from _pytest.fixtures import SubRequest
    from rich.console import Console

__all__ = ("TrackerPlugin",)


INDENT = "      "


def pytest_unconfigure(config: pytest.Config) -> None:
    if config.pluginmanager.hasplugin(TrackerPlugin.name):
        plugin = config.pluginmanager.get_plugin(TrackerPlugin.name)
        config.pluginmanager.unregister(plugin, TrackerPlugin.name)


def render_exception_info(excinfo: ExceptionInfo[BaseException]) -> ConsoleRenderable:
    import _pytest
    import pluggy
    from baloto.core.rich.tracebacks import from_exception

    tb = from_exception(excinfo.type, excinfo.value, excinfo.tb, suppress=(_pytest, pluggy))
    return Padding(tb, (0, 0, 0, 4))


def render_from_exception(exc_value: BaseException) -> ConsoleRenderable:
    import _pytest
    import pluggy
    import importlib
    from pathlib import Path
    from baloto.core.rich.tracebacks import from_exception

    collector_path = Path(__file__).parent / "collector"

    # width = MIN_WIDTH - len(INDENT)
    tb = from_exception(
        type(exc_value),
        exc_value,
        exc_value.__traceback__,
        suppress=(_pytest, pluggy, importlib, str(collector_path)),
        max_frames=1,
        # width=width,
    )
    return Padding(tb, (0, 0, 0, 4))


class TrackerPlugin(pytest.TerminalReporter):
    name: str = "hook-tracker"

    def __init__(self, config: pytest.Config) -> None:
        super().__init__(config)
        self.console: Console | None = None
        self.lock = threading.Lock()
        self.session_start: float = 0.0
        self.session_start_dt: pendulum.DateTime = pendulum.now()
        self.session_end: float = 0.0
        self.session_end_dt: pendulum.DateTime = pendulum.now()
        self.reporter: Reporter | None = None
        self.pytest_env: PytestEnvironment | None = None

    # def get_verbosity(self, value: str) -> int:
    #     return self.config.get_verbosity(value)
    #
    # verbosity_assertions = partialmethod(get_verbosity, value=pytest.Config.VERBOSITY_ASSERTIONS)
    # verbosity_test_case = partialmethod(get_verbosity, value=pytest.Config.VERBOSITY_TEST_CASES)

    @pytest.hookimpl(tryfirst=True)
    def pytest_addhooks(self, pluginmanager: pytest.PytestPluginManager) -> None:
        return None

    def pytest_plugin_registered(self, plugin: object) -> None:
        name = self.config.pluginmanager.get_name(plugin)
        if name is None or self.verbosity <= 0:
            return None

        hm = HookMessage("pytest_plugin_registered").add_info(name)
        if not self.config.option.traceconfig:
            if name in ["hook-tracker", "baloto-tracker", "baloto-logging"]:
                self.console.print(hm)
                return None
        hm = HookMessage("pytest_plugin_registered").add_info(name)
        self.console.print(hm)

    @pytest.hookimpl(trylast=True)
    def pytest_configure(self, config: pytest.Config) -> None:
        config.option.verbose = int(settings.verbosity.value)
        from tests import get_console_key

        console_key = get_console_key()
        self.console = config.stash.get(console_key, None)
        self.reporter = Reporter(config, self.console)

    @pytest.hookimpl
    def pytest_sessionstart(self, session: pytest.Session) -> None:
        import pendulum
        import platform

        self.session_start = timing.Instant()
        self.session_start_dt = pendulum.now()
        # TODO: remove after fully override
        setattr(self, "_session", session)
        setattr(self, "_session_start", self.session_start)

        if not self.showheader:
            return

        session.name = "Baloto UnitTesting"
        self.console.rule(f"Session '{session.name}' starts", characters="=")
        self.reporter.report_session_start(session, self.session_start_dt)

        from tests.plugins.tracker.header import build_environment

        environment = build_environment(config=self.config)
        if not self.no_header:
            self.reporter.report_header(environment)

    @pytest.hookimpl(trylast=True)
    def pytest_report_header(self, config: pytest.Config) -> list[tuple[str, Any]]:
        if self.verbosity > 0:
            hm = HookMessage("pytest_report_header")
            self.console.print(hm)
        result = []

        if config.inipath:
            configfile = Path(config.inipath).relative_to(config.rootpath).as_posix()
            result.append(("configfile", configfile))

        if config.args_source == pytest.Config.ArgsSource.TESTPATHS:
            testpaths: list[str] = config.getini("testpaths")
            result.append(("testpaths", ", ".join(testpaths)))

        return result

    @pytest.hookimpl(tryfirst=True)
    def pytest_exception_interact(
        self,
        node: pytest.Item | pytest.Collector,
        call: pytest.CallInfo[Any],
        report: pytest.CollectReport | pytest.TestReport,
    ) -> None:
        from tests.plugins.tracker.assert_report import AssertionErrorReport

        self.console.rule(
            f"[red bold]EXCEPTION INTERACT [dim]({call.excinfo.type})",
            style="red bold",
            align="center",
            characters="=",
        )

        if call.excinfo.type is AssertionError:
            try:
                aer = AssertionErrorReport(node, call, report)
                if aer.report_status:
                    self.console.print(aer)
                renderable = render_exception_info(call.excinfo)
                with self.lock:
                    self.console.print(renderable)

            except* AssertionReportException as e:
                self.console.print_exception()
                pass
        else:
            renderable = render_exception_info(call.excinfo)
            with self.lock:
                self.console.print(renderable)

    def _write_report_lines_from_hooks(self, lines: Sequence[str | Sequence[str]]) -> None:
        pass


def pytest_warning_recorded(
    warning_message: warnings.WarningMessage,
    when: Literal["config", "collect", "runtest"],
    nodeid: str,
    location: tuple[str, int, str] | None,
) -> None: ...


def pytest_fixture_setup(
    fixturedef: pytest.FixtureDef[Any], request: SubRequest
) -> object | None: ...


# from pathlib import Path
# import _pytest
# import pluggy
# import importlib
#
# collector_path = Path(__file__).parent / "collector"
# width = MIN_WIDTH - len(INDENT)
# tb = Traceback.from_exception(
#     type(BaseException),
#     exc_value,
#     exc_value.__traceback__,
#     suppress=(_pytest, pluggy, importlib, str(collector_path)),
#     max_frames=1,
#     width=width,
#     show_locals=False
# )
# from rich.padding import Padding
# return Padding(tb, (0, 0, 0, 4))
