"""
PYTEST_DONT_REWRITE
"""

# — Project : baloto-colombia
# — File Name : plugin.py
# — Dir Path : tests/plugins/error_reporter
# — Created on: 2025–06–04 at 12:36:22.

from __future__ import annotations

import sys
import threading
import warnings
from functools import partialmethod
from typing import Any
from typing import Literal
from typing import TYPE_CHECKING

import pytest
from rich.console import ConsoleRenderable
from rich.padding import Padding

from baloto.cleo.io.outputs.output import Verbosity
from baloto.core.config.settings import settings
from helpers import cleanup_factory
from plugins.tracker.assert_report import AssertionReportException

if TYPE_CHECKING:
    from _pytest._code.code import ExceptionInfo
    from _pytest.fixtures import SubRequest
    from rich.console import Console

__all__ = ("TrackerPlugin",)


INDENT = "    "
PLUGIN_NAME = "miloto-tracker"


@pytest.hookimpl
def pytest_configure(config: pytest.Config) -> None:
    from tests import get_console_key

    console_key = get_console_key()
    console = config.stash.get(console_key, None)

    tracker = TrackerPlugin(config, console)
    config.pluginmanager.register(tracker, TrackerPlugin.name)
    config.add_cleanup(cleanup_factory(config, tracker))


def pytest_unconfigure(config: pytest.Config) -> None:
    if config.pluginmanager.hasplugin(TrackerPlugin.name):
        plugin = config.pluginmanager.get_plugin(TrackerPlugin.name)
        config.pluginmanager.unregister(plugin, TrackerPlugin.name)


class TrackerPlugin:
    name: str = "hook-tracker"

    def __init__(self, config: pytest.Config, console: Console) -> None:
        self.config = config
        self.console = console
        self.lock = threading.Lock()

    @property
    def max_frames(self) -> int | None:
        # if is_pydevd_mode():
        #     return None
        print(self.config.option.verbose)
        print(self.config.option.verbose)
        print(self.config.option.verbose)
        print(self.config.option.verbose)
        print(self.config.option.verbose)
        print(self.config.option.verbose)
        print(self.config.option.verbose)
        print(self.config.option.verbose)
        print(self.config.option.verbose)
        print(self.config.option.verbose)
        max_frames = 50
        if self.config.option.verbose == Verbosity.NORMAL:
            max_frames = 2
        elif self.config.option.verbose == Verbosity.DEBUG:
            max_frames = None
        return max_frames

    @property
    def global_verbosity(self) -> int:
        return self.config.getoption("verbose", default=0)

    def get_verbosity(self, value: str) -> int:
        return self.config.get_verbosity(value)

    verbosity_assertions = partialmethod(get_verbosity, value=pytest.Config.VERBOSITY_ASSERTIONS)
    verbosity_test_case = partialmethod(get_verbosity, value=pytest.Config.VERBOSITY_TEST_CASES)

    @pytest.hookimpl
    def pytest_configure(self, config: pytest.Config) -> None: ...

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
                renderable = self.render_exception_info(call.excinfo)
                with self.lock:
                    self.console.print(renderable)

            except* AssertionReportException as e:
                self.console.print_exception()
                pass
        else:
            renderable = self.render_exception_info(call.excinfo)
            with self.lock:
                self.console.print(renderable)

    def render_exception_info(self, excinfo: ExceptionInfo[BaseException]) -> ConsoleRenderable:

        import _pytest
        import pluggy

        tb = traceback(
            self.config,
            extract(self.config, excinfo.type, excinfo.value, excinfo.tb),
            suppress=(_pytest, pluggy),
            width=None,
            max_frames=self.max_frames,
        )
        return Padding(tb, (0, 0, 0, 4))
        # return tb

    def render_from_exception(self, exc: BaseException) -> ConsoleRenderable:
        import _pytest
        import pluggy
        import importlib
        from pathlib import Path

        collector_path = Path(__file__).parent / "collector"
        width = MIN_WIDTH - len(INDENT)
        tb = from_exception(
            self.config,
            type(exc),
            exc,
            exc.__traceback__,
            suppress=(_pytest, pluggy, importlib, str(collector_path)),
            max_frames=1,
            width=width,
        )
        return Padding(tb, (0, 0, 0, 4))

    def pytest_unconfigure(self, config: pytest.Config) -> None: ...


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
