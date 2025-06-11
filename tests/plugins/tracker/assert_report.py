# Project : baloto-colombia
# User Naem : solma
# File Name : assert_report.py
# Dir Path : tests:
# Created on: 2025-06-02 at 00:54:42.

from __future__ import annotations

import itertools
import linecache
import sys
import warnings
from pathlib import Path
from typing import Any
from typing import TYPE_CHECKING

import pendulum
import pytest
from rich import box
from rich.columns import Columns
from rich.panel import Panel
from rich.scope import render_scope
from rich.style import Style
from rich.syntax import Syntax
from rich.table import Table
from rich.traceback import PathHighlighter
from rich.traceback import Stack

from baloto.cleo.rich.theme import MilotoSyntaxTheme
from baloto.cleo.rich.theme import MilotoTheme
from plugins.tracebacks import TracebackOptions
from plugins.tracebacks import extract

if TYPE_CHECKING:
    from rich.console import Console, ConsoleOptions, RenderResult


class AssertionReportException(Exception):
    pass


from rich.traceback import Traceback, Frame


# noinspection PyUnusedLocal
class AssertionErrorReport:
    """Reports an assertion error"""

    def __init__(
        self,
        node: pytest.Item | pytest.Collector,
        call: pytest.CallInfo[Any],
        report: pytest.CollectReport | pytest.TestReport,
        raise_exceptions: bool = True,
    ) -> None:

        self._can_render_report = True
        if call.excinfo.type is None or call.excinfo.value is None or call.excinfo.tb is None:  # type: ignore[union-attr]
            msg = "Value for 'call.excinfo.type' and 'call.excinfo.value' are required tfor render the report."
            if raise_exceptions:
                raise ValueError(msg)
            else:
                self._can_render_report = False
                warnings.warn(msg, category=RuntimeWarning, stacklevel=2)
                return

        self._node = node
        self._call = call
        self._report = report
        self._frame: Frame | None = None
        self._stack: Stack | None = None
        getoption = node.config.getoption

        err_msg = "Could not locate the matching pytest FrameSummary"
        longrepr = getattr(report, "longrepr")
        from ..tracebacks import TracebackOptions

        showlocals = getoption(TracebackOptions.SHOW_LOCALS)
        trace = extract(node.config, call.excinfo.type, call.excinfo.value, call.excinfo.tb)
        crash_lineno = longrepr.reprcrash.lineno
        crash_path = longrepr.reprcrash.path
        predicate = lambda x: x.lineno == crash_lineno and x.filename == crash_path
        for stack in trace.stacks:
            self._frame = next(filter(predicate, reversed(stack.frames)), None)
            if self._frame:
                if not stack.exc_value:
                    stack.exc_value = call.excinfo.value
                self._stack = stack
                break

        if not self._frame:
            if raise_exceptions:
                raise AssertionReportException("Could not locate the matching Frame/FrameSummary")
            else:
                warnings.warn(err_msg, category=RuntimeWarning, stacklevel=2)
                self._can_render_report = False
                return
        else:
            from traceback import extract_tb

            stack_summary = extract_tb(self._call.excinfo.tb)  # type: ignore[union-attr]
            extracted_tb = next(filter(predicate, reversed(stack_summary)), None)
            self._frame.line = extracted_tb.line
            self._frame.line = str(call.excinfo.value)
            self._frame.end_lineno = extracted_tb.end_lineno

    @property
    def report_status(self) -> bool:
        return self._can_render_report

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:

        config = self._node.config
        frame = self._frame
        stack = self._stack
        func_linkpath = ""
        border_style = "bright_blue dim"
        path_highlighter = PathHighlighter()

        table = Table(
            title="AssertionError Report",
            caption="Triggered by [bright_blue]pytest_exception_interact[/] pytest hook",
            box=box.HORIZONTALS,
            collapse_padding=False,
            show_header=True,
            expand=True,
            style="grey42",
            header_style="light_goldenrod2",
            title_style="b",
            caption_style="gray46",
            title_justify="center",
            caption_justify="left",
            highlight=True,
        )
        from rich.padding import Padding

        table.add_column("Topic", min_width=20, style="b i", max_width=25, justify="left")
        table.add_column("Value")

        table.add_row("EXCEPTION INFORMATION", style=Style(color="bright_cyan", italic=False))
        line_text = console.render_str(frame.line, justify="left")
        line_text.highlight_words(["Expected:", "but:"], style="i cyan")
        # width=config.getoption(TracebackOptions.CODE_WIDTH) + 10
        panel = Panel(
            line_text,
            title="[bright_white]error message",
            expand=True,
            box=box.DOUBLE,
            width=options.max_width - 50,
            padding=1,
            border_style=border_style,
        )

        table.add_row("Error Message", panel, style="none")

        from ..logging import LoggingOptions

        enable_link_path = config.getoption(LoggingOptions.ENABLE_LINK_PATH)

        table.add_row("File", path_highlighter(self._report.fspath))
        if enable_link_path:
            _, lineno, _ = self._node.location  # type: ignore[union-attr]
            table.add_row("Location", f"{Path(self._report.fspath).as_posix()}:{lineno}")

        originalname = frame.name
        function = console.render_str(f"{originalname}()", style="repr.call")
        table.add_row("Function", function)
        if enable_link_path:
            if not sys.stdout.isatty():
                table.add_row("Raise Location Line", f"{self._node.path.as_posix()}:{frame.lineno}")
            else:
                linkname = f"{originalname}_{frame.lineno}"
                func_linkpath = f"[link={self._node.path.as_posix()}:{frame.lineno}][blue u]{linkname}[/link][/] <-click"
                table.add_row("Raise Location Line", "[bright_blue]" + func_linkpath + "[/]")

        fullsource = linecache.getlines(str(self._node.path))
        code = "".join(fullsource)
        theme = config.getoption(TracebackOptions.THEME) or MilotoTheme()
        background_color = None
        if theme is MilotoTheme:
            background_color = MilotoSyntaxTheme().get_background_style()

        extra_lines = config.getini(TracebackOptions.EXTRA_LINES)
        syntax = Syntax(
            code,
            "python",
            line_numbers=True,
            indent_guides=True,
            dedent=False,
            theme=theme,
            code_width=options.max_width - 60,
            background_color=background_color,
            highlight_lines={frame.lineno},
            line_range=(
                frame.lineno - extra_lines,
                frame.end_lineno + extra_lines,
            ),
        )
        panel = Panel(
            syntax,
            title="[bright_white]failed assertion",
            expand=False,
            box=box.DOUBLE,
            width=options.max_width - 50,
            border_style="bright_blue dim",
        )
        table.add_row("Exc. Stack Frame", panel)

        table.add_section()
        table.add_row("TEST INFORMATION", style=Style(color="bright_cyan", italic=False))
        if self._node.name == originalname:
            table.add_row("Test Name", f"[green]originalname[/]")
        else:
            table.add_row("Test Original Name", originalname)
            table.add_row("Test ID", self._node.name)

        table.add_row("pytest_runtestloop::when", "[bright_blue b]" + self._report.when + "[/]")

        duration = pendulum.duration(seconds=self._report.duration)
        table.add_row("Test Duration", f"{self._report.duration} aprox: {duration.in_words()}")

        if enable_link_path and sys.stdout.isatty():
            table.add_row("Test Location", "[bright_blue]" + func_linkpath + "[/]")

        if getattr(self._node, "user_properties"):
            user_properties = dict(map(lambda x: (x[0], x[1]), self._report.user_properties))
            renderable = render_scope(
                user_properties, title="[i]user properties", indent_guides=False, sort_keys=True
            )
            table.add_row("User Properties", renderable)

        # -- Handling markers if Any
        if self._node.own_markers:
            func = lambda marker: f"{marker[0]}. [bright_yellow]@{marker[1].name}[/]"
            markers = list(
                map(func, list(zip(itertools.count(start=1, step=1), self._node.own_markers)))
            )
            column = Columns(markers, column_first=True, equal=True, padding=1)
            table.add_row("Markers", column)

            # -- Handling parametrize marker if any
            if self._node.get_closest_marker("parametrize"):
                callspec = getattr(self._node, "callspec")
                param_names = callspec.params
                renderable = render_scope(param_names, title="parameters", indent_guides=True)
                table.add_row("Parameters", renderable)

        if self._stack.notes:
            table.add_section()
            for note in self._stack.notes:
                table.add_row("Note", "[i bright_white]" + note + "[/]")

        yield table
        yield ""
