"""
PYTEST_DONT_REWRITE
"""

# — Project : baloto-colombia
# — File Name : plugin.py
# — Dir Path : tests/plugins/error_reporter
# — Created on: 2025–06–04 at 12:36:22.

from __future__ import annotations

import threading
import time
from collections.abc import Generator
from collections.abc import Sequence
from pathlib import Path
from typing import Any
from typing import TYPE_CHECKING

import pytest
from rich.console import ConsoleRenderable
from rich.padding import Padding
from rich.segment import ControlType
from rich.style import Style
from rich.text import Text
from typing_extensions import deprecated

from baloto.core import richer
from plugins.tracker.header import PytestEnvironment
from plugins.pytest_richtrace.models import TestRunResults

if TYPE_CHECKING:
    from baloto import RichConfig
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

    tb = from_exception(excinfo.type, excinfo.value, excinfo.tb, suppress=(_pytest, pluggy))
    return Padding(tb, (0, 0, 0, 4))


def render_from_exception(exc_value: BaseException) -> ConsoleRenderable:
    import _pytest
    import pluggy
    import importlib
    from pathlib import Path

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

        self._pytest_config = config
        self._rich_config: RichConfig | None = None
        self.rootpath = config.rootpath
        self.console: Console | None = None
        self._lock = threading.Lock()
        self.test_results: TestRunResults | None = None

        self._register_plugins(config)

    def _register_plugins(self, config: pytest.Config) -> None:

        from plugins.tracker.collection_plugin import CollectionObserver

        self.collector = CollectionObserver()
        config.pluginmanager.register(self.collector, name="richtrace-collection")

        from plugins.tracker.text_execution_plugin import TestExecutionObserver

        self.runtest = TestExecutionObserver()
        config.pluginmanager.register(self.runtest, name="richtrace-testrun")


    @pytest.hookimpl(trylast=True)
    def pytest_sessionstart(self, session: pytest.Session) -> None:
        from pydantic_extra_types.pendulum_dt import DateTime

        precise_start = time.perf_counter()
        start = DateTime.now()
        self.test_results = TestRunResults(start=start, precise_start=precise_start)

        # TODO: remove after fully override
        setattr(self, "_session", session)
        setattr(self, "_session_start", self.test_results.precise_start)
        richer.RichPluginManager.get_plugin_manager().register(self, self.name)

    @pytest.hookimpl(specname="pytest_sessionstart", tryfirst=True)
    def sessionstart_first(self, session: pytest.Session) -> None:
        pass

    #
    #     self.test_results.precise_start = time.perf_counter()
    #     self.test_results.start = DateTime.now()
    #
    #     # TODO: remove after fully override
    #     setattr(self, "_session", session)
    #     setattr(self, "_session_start", self.test_results.precise_start)
    #
    #     if not self.showheader:
    #         return
    #
    #     session.name = "Baloto UnitTesting"
    #     self.console.rule(f"Session '{session.name}' starts", characters="=")
    #     self.reporter.report_session_start(session, self.test_results.start)
    #
    #     from tests.plugins.tracker.header import build_environment
    #
    #     environment = build_environment(config=self.config)
    #     if not self.no_header:
    #         self.reporter.report_header(environment)
    #
    @pytest.hookimpl(specname="pytest_sessionstart", trylast=True)
    def sessionstart_last(self, session: pytest.Session) -> None:
        self.test_results.precise_start = time.perf_counter()

    #     self.test_results.start = DateTime.now()
    #

    #
    #     if not self.showheader:
    #         return
    #
    #     session.name = "Baloto UnitTesting"
    #     self.console.rule(f"Session '{session.name}' starts", characters="=")
    #     self.reporter.report_session_start(session, self.test_results.start)
    #
    #     from tests.plugins.tracker.header import build_environment
    #
    #     environment = build_environment(config=self.config)
    #     if not self.no_header:
    #         self.reporter.report_header(environment)


class TrackerPluginnininin:
    name: str = "hook-tracker"

    def __init__(self, config: pytest.Config) -> None:
        super().__init__(config)

        self.pytest_env: PytestEnvironment | None = None
        self._text_to_overwrite: str | None = None

    @pytest.hookimpl(wrapper=True)
    def pytest_sessionfinish(
        session: pytest.Session, exitstatus: int | pytest.ExitCode
    ) -> Generator[None]:
        pass

    @pytest.hookimpl(wrapper=True)
    def pytest_terminal_summary(self) -> Generator[None]:
        pass

    @pytest.hookimpl
    def pytest_sessionstart(self, session: pytest.Session) -> None:
        from pydantic_extra_types.pendulum_dt import DateTime

        self.test_results.precise_start = time.perf_counter()
        self.test_results.start = DateTime.now()

        # TODO: remove after fully override
        setattr(self, "_session", session)
        setattr(self, "_session_start", self.test_results.precise_start)

        if not self.showheader:
            return

        session.name = "Baloto UnitTesting"
        self.console.rule(f"Session '{session.name}' starts", characters="=")
        self.reporter.report_session_start(session, self.test_results.start)

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

    def _write_report_lines_from_hooks(self, lines: Sequence[str | Sequence[str]]) -> None:
        pass

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

    def write_sep(
        self,
        sep: str,
        title: str | None = None,
        fullwidth: int | None = None,
        **markup: bool,
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
        print_key_value(self.console, "internal error", line, prefix=INDENT, key_color="bold red")


def pytest_fixture_setup(
    fixturedef: pytest.FixtureDef[Any], request: SubRequest
) -> object | None: ...


# class RichTracebacks:
#     def __init__(self, config: RichConfig) -> None:
#         self.config = config
#
#     def from_exception(
#             self,
#             exc_type: Type[BaseException] | None,
#             exc_value: BaseException,
#             tb: TracebackType | None = None,
#             *,
#             width: int | None= settings.tracebacks.width,
#             code_width: int = settings.tracebacks.code_width,
#             extra_lines: int = settings.tracebacks.extra_lines,
#             word_wrap: bool = settings.tracebacks.word_wrap,
#             show_locals: bool = settings.tracebacks.show_locals,
#             locals_max_length: int = settings.tracebacks.max_length,
#             locals_max_string: int = settings.tracebacks.max_string,
#             locals_hide_dunder: bool = settings.tracebacks.hide_dunder,
#             locals_hide_sunder: bool = settings.tracebacks.hide_sunder,
#             indent_guides: bool = settings.tracebacks.indent_guides,
#             suppress: Iterable[str | ModuleType] = (),
#             max_frames: int = settings.tracebacks.max_frames,
#     ) -> ConsoleRenderable:
#
#         if exc_type is None:
#             exc_type = BaseException
#         if tb is None:
#             tb = exc_value.__traceback__
#
#         trace = Traceback.extract(
#             exc_type,
#             exc_value,
#             tb,
#             show_locals=show_locals,
#             locals_max_length=locals_max_length,
#             locals_max_string=locals_max_string,
#             locals_hide_dunder=locals_hide_dunder,
#             locals_hide_sunder=locals_hide_sunder,
#         )
#         # width = MIN_WIDTH - len(INDENT)
#         tb = Traceback(trace=trace)
#         tb.width = width
#         tb.code_width = code_width
#         tb.extra_lines = extra_lines
#         tb.word_wrap = word_wrap
#         tb.show_locals = show_locals
#         tb.locals_max_length = show_locals
#         tb.locals_max_string = locals_max_string
#         tb.locals_hide_dunder = locals_hide_dunder
#         tb.locals_hide_sunder = locals_hide_sunder
#         tb.indent_guides = indent_guides
#         tb.max_frames = max_frames
#         tb.theme = settings.syntax_theme
#         tb.suppress = suppress
#
#         return tb

# def traceback(self) -> ConsoleRenderable:
#     exc_type, exc_value, tb = sys.exc_info()
#     if exc_type is None or exc_value is None or tb is None:
#         raise ValueError("Value for 'trace' required if not called in except: block")
#     return self.from_exception(exc_type, exc_value, tb)
