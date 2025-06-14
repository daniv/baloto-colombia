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
import time
import warnings
from abc import ABC
from abc import abstractmethod
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
from circuits import Component
import pendulum
import pytest
from rich.console import ConsoleRenderable
from rich.padding import Padding
from _pytest import timing
from rich.segment import ControlType
from rich.style import Style
from rich.text import Text
from typing_extensions import deprecated

from baloto.core.config.settings import settings
from baloto.core.rich.testers.messages import HookMessage
from plugins.tracker.assert_report import AssertionReportException
from plugins.tracker.header import PytestEnvironment
from plugins.tracker.models import TestRunResults
from plugins.tracker.reporter import Reporter

if TYPE_CHECKING:
    import _pytest._code as pytest_code
    from _pytest.fixtures import SubRequest
    from rich.console import Console

__all__ = ("TrackerPlugin",)


INDENT = "      "


def pytest_unconfigure(config: pytest.Config) -> None:
    if config.pluginmanager.hasplugin(TrackerPlugin.name):
        plugin = config.pluginmanager.get_plugin(TrackerPlugin.name)
        config.pluginmanager.unregister(plugin, TrackerPlugin.name)


@deprecated("Not should be used")
def render_exception_info(excinfo: pytest.ExceptionInfo[BaseException]) -> ConsoleRenderable:
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

        self.config = config
        self.rootpath = config.rootpath
        self.console: Console | None = None
        self.console: Console | None = None
        self._lock = threading.Lock()
        self.test_results = TestRunResults()
        self.reporter: Reporter | None = None

        self.results = TestRunResults(run_id=self.run_id)
        self._create_plugins(config)

    def _create_plugins(self, config: pytest.Config) -> None:
        from baloto.core.tester.rich_testers import rich_plugin_manager, cleanup_factory

        from plugins.tracker.collection_plugin import CollectionObserver
        self.collector = CollectionObserver()
        config.pluginmanager.register(self.collector, name="richtrace-collection")
        rich_plugin_manager().register(self.collector, name="richtrace-collection")
        config.add_cleanup(cleanup_factory(self.collector))

        from plugins.tracker.text_execution_plugin import TestExecutionObserver
        self.runtest = TestExecutionObserver()
        rich_plugin_manager().register(self.collector, name="richtrace-testrun")
        config.add_cleanup(cleanup_factory(self.runtest))

        from plugins.tracker.reporter_plugin import ReporterPlugin
        self.writer = ReporterPlugin(config, self.console)
        config.pluginmanager.register(self.writer, name="richtrace-richreporter")
        config.add_cleanup(cleanup_factory(self.writer))




class TrackerPlugin1(pytest.TerminalReporter):
    name: str = "hook-tracker"

    def __init__(self, config: pytest.Config) -> None:
        super().__init__(config)






        self.pytest_env: PytestEnvironment | None = None
        self._text_to_overwrite: str | None = None

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
        from pydantic_extra_types.pendulum_dt import DateTime

        self._test_results.precise_start = time.perf_counter()
        self._test_results.start = DateTime.now()

        # TODO: remove after fully override
        setattr(self, "_session", session)
        setattr(self, "_session_start", self._test_results.precise_start)

        if not self.showheader:
            return

        session.name = "Baloto UnitTesting"
        self.console.rule(f"Session '{session.name}' starts", characters="=")
        self.reporter.report_session_start(session, self._test_results.start)

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

    @pytest.hookimpl
    def pytest_collection(self) -> None:
        msg = "collecting ... "
        if self.isatty:
            if self.config.option.verbose >= 0:
                text = self.console.render_str(msg, style="bold")
                self._text_to_overwrite = text.markup
                self.console.print(text.markup, end="")
                self.console.file.flush()
        elif self.config.option.verbose >= 1:
            self.console.print(msg, style="bold")
            self.console.file.flush()

    def pytest_collectreport(self, report: CollectReport) -> None:
        if report.failed:
            self._add_stats("error", [report])
        elif report.skipped:
            self._add_stats("skipped", [report])
        items = [x for x in report.result if isinstance(x, Item)]
        self._numcollected += len(items)
        if self.isatty:
            self.report_collect()

    def no_rewrite(self, line: str) -> None:
        from rich.control import Control

        if line:
            self.console.control(Control((ControlType.ERASE_IN_LINE, 2)))
            self.console.control(Control((ControlType.CURSOR_MOVE_TO_COLUMN, 0)))
            self.console.file.write(line)
        else:
            fill_count = self.console.width - len(line) - 1
            fill = " " * fill_count
            line = str(line)
            self.console.file.write("\r" + line + fill)

    def pytest_collection_finish(self, session: pytest.Session) -> None:
        super().pytest_collection_finish(session=session)
        pass

    # @pytest.hookimpl(tryfirst=True)
    def pypytest_exception_interact(
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
            excrepr: pytest_code.code.ExceptionRepr,
            excinfo: pytest.ExceptionInfo[BaseException],
    ) -> bool | None:
        self.console.rule(f"[red bold]INTERNAL ERROR [dim]({excinfo.typename})", style="red bold", align="center", characters="=")

        repr_file = Path(excrepr.reprcrash.path).relative_to(self.config.rootpath).as_posix()
        if settings.tracebacks.isatty_link:
            from baloto.core.rich import create_link_markup
            linkname = create_link_markup(excrepr.reprcrash.path, excrepr.reprcrash.lineno)
        else:
            linkname = f"{Path(excrepr.reprcrash.path).as_posix()}:{excrepr.reprcrash.lineno}"
        hook_message = (
            HookMessage("pytest_internalerror")
            .add_info(excinfo.typename)
            .add_key_value("reprcrash.lineno", str(excrepr.reprcrash.lineno), value_color="repr")
            .add_key_value("reprcrash.message", str(excrepr.reprcrash.message))
            .add_key_value("reprcrash.path", repr_file, value_color="none")
            .add_key_value("location", linkname, value_color="none", escape_markup=False)
            .add_key_value("reprtraceback.style", excrepr.reprtraceback.style)
            .add_key_value("showing locals", str(self.config.option.showlocals), value_color="none")
        )
        self.console.print(hook_message)
        return self.reporter.report_internalerror(excrepr, excinfo)

    def nowrite(self, content: str, *, flush: bool = False, **markup: bool) -> None:
        bold = False
        if "bold" in markup:
            bold = True

        self.console.print(content, style=Style(color="white", bold=bold))

    def nowrite_line(self, line: str | bytes, **markup: bool) -> None:
        if self.console:
            self.console.print(line)
        else:
            print("EARLY PLUGIN:", line, end="")

    def write_sep(self, sep: str, title: str | None = None, fullwidth: int | None = None,  **markup: bool,
    ) -> None:
        color = "white"
        if "green" in markup:
            color = "green"
        elif "red" in markup:
            color = "red"
        from_ansi = Text.from_ansi(title)
        self.console.rule(title=from_ansi.markup, style=color)




def render_exception_repr(self, excrepr: pytest_code.code.ExceptionRepr) -> None:
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


class RichTracebacks:
    def __init__(self, config: RichConfig) -> None:
        self.config = config

    def from_exception(
            self,
            exc_type: Type[BaseException] | None,
            exc_value: BaseException,
            tb: TracebackType | None = None,
            *,
            width: int | None= settings.tracebacks.width,
            code_width: int = settings.tracebacks.code_width,
            extra_lines: int = settings.tracebacks.extra_lines,
            word_wrap: bool = settings.tracebacks.word_wrap,
            show_locals: bool = settings.tracebacks.show_locals,
            locals_max_length: int = settings.tracebacks.max_length,
            locals_max_string: int = settings.tracebacks.max_string,
            locals_hide_dunder: bool = settings.tracebacks.hide_dunder,
            locals_hide_sunder: bool = settings.tracebacks.hide_sunder,
            indent_guides: bool = settings.tracebacks.indent_guides,
            suppress: Iterable[str | ModuleType] = (),
            max_frames: int = settings.tracebacks.max_frames,
    ) -> ConsoleRenderable:

        if exc_type is None:
            exc_type = BaseException
        if tb is None:
            tb = exc_value.__traceback__

        trace = Traceback.extract(
            exc_type,
            exc_value,
            tb,
            show_locals=show_locals,
            locals_max_length=locals_max_length,
            locals_max_string=locals_max_string,
            locals_hide_dunder=locals_hide_dunder,
            locals_hide_sunder=locals_hide_sunder,
        )
        # width = MIN_WIDTH - len(INDENT)
        tb = Traceback(trace=trace)
        tb.width = width
        tb.code_width = code_width
        tb.extra_lines = extra_lines
        tb.word_wrap = word_wrap
        tb.show_locals = show_locals
        tb.locals_max_length = show_locals
        tb.locals_max_string = locals_max_string
        tb.locals_hide_dunder = locals_hide_dunder
        tb.locals_hide_sunder = locals_hide_sunder
        tb.indent_guides = indent_guides
        tb.max_frames = max_frames
        tb.theme = settings.syntax_theme
        tb.suppress = suppress

        return tb

    def traceback(self) -> ConsoleRenderable:
        exc_type, exc_value, tb = sys.exc_info()
        if exc_type is None or exc_value is None or tb is None:
            raise ValueError("Value for 'trace' required if not called in except: block")
        return self.from_exception(exc_type, exc_value, tb)
