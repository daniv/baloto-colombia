"""
PYTEST_DONT_REWRITE
"""
# — Project : baloto-colombia
# — File Name : plugin.py
# — Dir Path : tests/plugins/error_reporter
# — Created on: 2025–06–04 at 12:36:22.

from __future__ import annotations

import warnings
from typing import TYPE_CHECKING, Any, Literal

import pytest
from rich.console import Console, ConsoleRenderable

from baloto.cleo.rich.factory.console_factory import ConsoleFactory
from baloto.cleo.utils import markup_path
from helpers import cleanup_factory
from plugins.tracker.assert_report import AssertionReportException
from plugins.tracker.console import print_hook_info, print_separator, print_key_value

if TYPE_CHECKING:
    from _pytest._code.code import ExceptionInfo
    from _pytest.fixtures import SubRequest

__all__ = ( )


INDENT = "    "
MIN_WIDTH = 120
PLUGIN_NAME = "miloto-tracker"

@pytest.hookimpl
def pytest_configure(config: pytest.Config) -> None:
    from tests import get_console_key

    console_key = get_console_key()
    console = config.stash.get(console_key, None)
    if console is None:
        console = ConsoleFactory.console_output()
        config.stash.setdefault(console_key, console)

    tracker = TrackerPlugin(config, console)
    config.pluginmanager.register(tracker, TrackerPlugin.name)

    config.add_cleanup(cleanup_factory(config, tracker))


class TrackerPlugin:
    name: str = "pytest-hook-tracker"

    def __init__(self, config: pytest.Config, console: Console) -> None:
        self.config = config
        self.console = console

    @property
    def verbosity(self) -> int:
        return self.config.option.verbosity

    @property
    def enable_link_path(self) -> bool:
        return self.config.option.enable_link_path

    @property
    def code_width(self) -> int:
        return self.config.option.tracebacks_code_width

    @property
    def locals_max_length(self) -> int:
        return self.config.option.tracebacks_locals_max_length

    @property
    def locals_max_string(self) -> int:
        return self.config.option.tracebacks_locals_max_string

    @property
    def width(self) -> int:
        return self.config.option.tracebacks_width

    @property
    def extra_lines(self) -> int:
        return self.config.option.tracebacks_extra_lines

    @property
    def locals_hide_dunder(self) -> bool:
        return self.config.option.tracebacks_locals_hide_dunder

    @property
    def locals_hide_sunder(self) -> bool:
        return self.config.option.tracebacks_locals_hide_sunder

    @property
    def theme(self) -> str:
        return self.config.option.tracebacks_theme or "ansi_dark"

    @property
    def word_wrap(self) -> bool:
        return self.config.option.tracebacks_word_wrap

    @property
    def show_locals(self) -> bool:
        return self.config.option.tracebacks_show_locals

    @property
    def indent_guides(self) -> bool:
        return self.config.option.tracebacks_indent_guides

    @pytest.hookimpl
    def pytest_configure(self, config: pytest.Config) -> None:
        ...

    @pytest.hookimpl(tryfirst=True)
    def pytest_exception_interact(
            self,
        node: pytest.Item | pytest.Collector,
        call: pytest.CallInfo[Any],
        report: pytest.CollectReport | pytest.TestReport,
    ) -> None:
        from tests.plugins.tracker.assert_report import AssertionErrorReport
        print_separator(
            self.console,
            f"[red bold]EXCEPTION INTERACT [dim]({call.excinfo.type})",
            style="red bold",
            align="center",
            characters="="
        )

        if call.excinfo.type is AssertionError:
            try:
                aer = AssertionErrorReport(node, call, report)
                if aer.report_status:
                    self.console.print(aer)
                    self.console.rule("[bright_red]Stack Trace", characters="=", style="bright_red dim")
                    renderable = self.render_exception_info(call.excinfo)
                    self.console.print(renderable)

            except* AssertionReportException as e:
                self.console.print_exception()
                pass
        else:
            renderable = self.render_exception_info(call.excinfo)
            self.console.print(renderable)

    def render_exception_info(self, excinfo: ExceptionInfo[BaseException]) -> ConsoleRenderable:
        from rich.traceback import Traceback
        import _pytest
        import pluggy

        return Traceback(
            Traceback.extract(
                exc_type=excinfo.type,
                exc_value=excinfo.value,
                traceback=excinfo.tb,
                show_locals=self.show_locals,
                locals_max_length=self.locals_max_length,
                locals_max_string=self.locals_max_string,
                locals_hide_dunder=self.locals_hide_dunder,
                locals_hide_sunder=self.locals_hide_sunder,
            ),
            width=self.width,
            theme=self.theme,
            suppress=(_pytest, pluggy),
            indent_guides=self.indent_guides,
            extra_lines=self.extra_lines,
            word_wrap=self.word_wrap,
            code_width=self.code_width,
            locals_max_string=self.locals_max_string,
            locals_max_length=self.locals_max_length
        )

    def render_from_exception(self, exc: BaseException) -> ConsoleRenderable:
        from rich.traceback import Traceback
        import _pytest
        import pluggy
        import importlib
        from pathlib import Path
        from rich.padding import Padding

        collector_path = Path(__file__).parent / "collector"
        width = MIN_WIDTH - len(INDENT)
        tb = Traceback.from_exception(
            type(BaseException),
            exc,
            exc.__traceback__,
            suppress=(_pytest, pluggy, importlib, str(collector_path)),
            max_frames=1,
            width=width,
            show_locals=self.show_locals,
            locals_max_length=self.locals_max_length,
            locals_hide_dunder=self.locals_hide_dunder,
            locals_hide_sunder=self.locals_hide_sunder,
        )
        return Padding(tb, (0, 0, 0, 4))

    def pytest_unconfigure(self, config: pytest.Config) -> None:
        ...



def pytest_warning_recorded(
    warning_message: warnings.WarningMessage,
    when: Literal["config", "collect", "runtest"],
    nodeid: str,
    location: tuple[str, int, str] | None,
) -> None:
    ...




def pytest_fixture_setup(
    fixturedef: pytest.FixtureDef[Any], request: SubRequest
) -> object | None:
    ...