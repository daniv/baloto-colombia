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
from rich.style import Style
from rich.text import Text

from baloto.core.config.settings import settings
from baloto.core.rich.testers.messages import HookMessage
from plugins.tracker.assert_report import AssertionReportException
from plugins.tracker.header import PytestEnvironment
from plugins.tracker.reporter import Reporter

if TYPE_CHECKING:
    from _pytest._code.code import ExceptionRepr
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

    @pytest.hookimpl(tryfirst=True)
    def pytest_internalerror(
            self,
            excrepr: ExceptionRepr,
            excinfo: ExceptionInfo[BaseException],
    ) -> bool | None:
        self.console.rule(f"[red bold]INTERNAL ERROR [dim]({excinfo.typename})", style="red bold", align="center", characters="=")


        show_locals = self.config.option.showlocals
        tb_style = excrepr.reprtraceback.style
        self._writer.print_hook_info("pytest_internalerror", info=f"tb-style: '{tb_style}'")
        self._writer.print_key_value("excinfo.typename", value=excinfo.typename, value_color="error")
        self._writer.print_key_value("excinfo.value", value=str(excinfo.value))
        path = splitdrive(Path(excrepr.reprcrash.path))
        self._writer.print_key_value("excrepr.path", value=path, value_color="repr")
        self._writer.print_key_value("excrepr.lineno", value=str(excrepr.reprcrash.lineno), value_color="repr")
        self._writer.print_key_value("excrepr.message", value=excrepr.reprcrash.message)
        self._writer.print_key_value("config.showlocals", value=str(show_locals), value_color="repr")
        if self.verbosity == 0:
            for line in str(excrepr).split("\n"):
                self._writer.print_key_value("internal error", line, key_color="bold red")
        elif self.verbosity == 1:
            self._writer.print_exc(excinfo.value)
        elif self.verbosity > 1:
            self._writer.print_exception_info(excinfo)

        return True

    def write(self, content: str, *, flush: bool = False, **markup: bool) -> None:
        bold = False
        if "bold" in markup:
            bold = True

        self.console.print(content, style=Style(color="white", bold=bold))

    def write_line(self, line: str | bytes, **markup: bool) -> None:
        self.console.print(line)

    def write_sep(self, sep: str, title: str | None = None, fullwidth: int | None = None,  **markup: bool,
    ) -> None:
        color = "white"
        if "green" in markup:
            color = "green"
        elif "red" in markup:
            color = "red"
        from_ansi = Text.from_ansi(title)
        self.console.rule(title=from_ansi.markup, style=color)


def render_exception_repr(self, excrepr: ExceptionRepr) -> None:
    for line in str(excrepr).split("\n"):
        print_key_value(
            self.console, "internal error", line, prefix=INDENT, key_color="bold red"
        )
def pytest_warning_recorded(
    warning_message: warnings.WarningMessage,
    when: Literal["config", "collect", "runtest"],
    nodeid: str,
    location: tuple[str, int, str] | None,
) -> None: ...


def pytest_fixture_setup(
    fixturedef: pytest.FixtureDef[Any], request: SubRequest
) -> object | None: ...
