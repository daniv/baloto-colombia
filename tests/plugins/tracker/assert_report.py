# Project : baloto-colombia
# User Naem : solma
# File Name : assert_report.py
# Dir Path : tests:
# Created on: 2025-06-02 at 00:54:42.

from __future__ import annotations

import itertools
import linecache
import warnings
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pendulum
import pytest
from pydantic import BaseModel, Field
from rich import box
from rich.columns import Columns
from rich.panel import Panel
from rich.scope import render_scope
from rich.style import Style
from rich.syntax import Syntax
from rich.table import Table

from baloto.cleo.formatters.formatter import Formatter
from baloto.cleo.utils import safe_str, markup_path

if TYPE_CHECKING:
    from argparse import Namespace
    from rich.console import Console, ConsoleOptions, RenderResult
    from traceback import FrameSummary


class AssertionReportException(Exception):
    pass


class Frame(BaseModel):
    filename: str
    lineno: int | None
    name: str
    line: str = ""
    instruction: tuple[int, int] = Field(default_factory=tuple)


class Stack(BaseModel):
    exc_type: str
    exc_value: str
    frame: Frame
    notes: list[str] = Field(default_factory=list)


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

        err_msg = "Could not locate the matching pytest FrameSummary"
        longrepr = getattr(report, "longrepr")
        frame_summary = self._frame_summary(longrepr.reprcrash.lineno, longrepr.reprcrash.path)
        if frame_summary:
            notes: list[str] = getattr(call.excinfo.value, "__notes__", None) or []

            self._stack = Stack(
                exc_type=safe_str(call.excinfo.type.__name__),
                exc_value=safe_str(call.excinfo.value),
                notes=notes,
                frame=Frame(
                    filename=frame_summary.filename or "?",
                    lineno=frame_summary.lineno,
                    name=frame_summary.name,
                    instruction=(frame_summary.lineno, frame_summary.end_lineno),
                ),
            )

        elif raise_exceptions:
            raise AssertionReportException("Could not locate the matching pytest FrameSummary")
        else:
            warnings.warn(err_msg, category=RuntimeWarning, stacklevel=2)
            self._can_render_report = False
            return

    @property
    def report_status(self) -> bool:
        return self._can_render_report

    @cached_property
    def namespace(self) -> Namespace:
        return self._node.config.option

    @property
    def enable_link_path(self) -> bool:
        return self.namespace.logging_enable_link_path

    @property
    def code_width(self) -> int:
        return self.namespace.tracebacks_code_width

    @property
    def theme(self) -> str:
        return self.namespace.tracebacks_theme or "ansi_dark"

    @property
    def word_wrap(self) -> bool:
        return self.namespace.tracebacks_word_wrap

    @property
    def extra_lines(self) -> int:
        return self.namespace.tracebacks_extra_lines

    def _frame_summary(self, lineno: int, path: str) -> FrameSummary | None:
        from traceback import extract_tb

        predicate = lambda x: x.lineno == lineno and x.filename == path
        stack_summary = extract_tb(self._call.excinfo.tb)  # type: ignore[union-attr]
        return next(filter(predicate, reversed(stack_summary)), None)

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:

        config = self._node.config
        func_linkpath = ""

        table = Table(
            title="AssertionError Report",
            caption="Triggered by [bright_blue]pytest_exception_interact[/] pytest hook",
            box=box.HORIZONTALS,
            collapse_padding=False,
            expand=False,
            show_header=True,
            style="grey42",
            # row_styles="",
            header_style="light_goldenrod2",
            title_style="b",
            caption_style="gray46",
            title_justify="center",
            caption_justify="left",
            highlight=True,
        )

        table.add_column("Topic", min_width=20, style="b i", max_width=25, justify="left")
        table.add_column("Value")

        table.add_row("EXCEPTION INFORMATION", style=Style(color="bright_cyan", italic=False))
        msg = self._stack.exc_value.strip()
        formatter = Formatter()
        formatter.set_text(msg)
        formatter.highlight_words(["Expected:", "but:"], style="i")
        panel = Panel(formatter.text.markup, title="error message", expand=False, padding=(0, 2), box=box.DOUBLE)
        table.add_row("Error Message", panel, style="none")

        text = markup_path(self._report.fspath)
        table.add_row("File", f"{text}")
        if self.enable_link_path:
            _, lineno, _ = self._node.location  # type: ignore[union-attr]
            table.add_row("Location", f"{Path(self._report.fspath).as_posix()}:{lineno}")
        originalname = self._stack.frame.name
        table.add_row("Function", originalname)
        if self.enable_link_path:
            linkname = f"{originalname}_{self._stack.frame.lineno}"
            func_linkpath = (
                f"[link={self._node.path.as_posix()}:{self._stack.frame.lineno}][blue u]{linkname}[/link][/] <-click"
            )
            table.add_row("Raise Location Line", "[bright_blue]" + func_linkpath + "[/]")

        fullsource = linecache.getlines(str(self._node.path))
        code = "".join(fullsource)

        _, last_line = self._stack.frame.instruction
        syntax = Syntax(
            code,
            "python",
            line_numbers=True, indent_guides=True, dedent=False, code_width=self.code_width, theme=self.theme,
            word_wrap=self.word_wrap, highlight_lines={self._stack.frame.lineno},
            line_range=(
                self._stack.frame.lineno - self.extra_lines,
                last_line + self.extra_lines,
            )
        )
        panel = Panel(syntax, title="failed assertion", expand=False, box=box.DOUBLE)
        table.add_row("stack frame", panel)

        table.add_section()
        table.add_row("TEST INFORMATION", style=Style(color="bright_cyan", italic=False))
        if self._node.name == originalname:
            table.add_row("Test Name", originalname)
        else:
            table.add_row("Test Original Name", originalname)
            table.add_row("Test ID", self._node.name)

        table.add_row("pytest_runtestloop::when", "[bright_blue b]" + self._report.when + "[/]")

        duration = pendulum.duration(seconds=self._report.duration)
        table.add_row("Test Duration", f"{self._report.duration} aprox: {duration.in_words()}")
        console.print(table)

        if self.enable_link_path:
            table.add_row("Test Location", "[bright_blue]" + func_linkpath + "[/]")

        if getattr(self._node, "user_properties"):
            user_properties = dict(map(lambda x: (x[0], x[1]), self._report.user_properties))
            renderable = render_scope(user_properties, title="[i]user properties", indent_guides=False, sort_keys=True)
            table.add_row("User Properties", renderable)

        # -- Handling markers if Any
        if self._node.own_markers:
            func = lambda marker: f"{marker[0]}. [bright_yellow]@{marker[1].name}[/]"
            markers = list(map(func, list(zip(itertools.count(start=1, step=1), self._node.own_markers))))
            column = Columns(markers, column_first=True, equal=True, padding=1)
            table.add_row("Markers", column)

            # -- Handling parametrize marker if any
            if self._node.get_closest_marker("parametrize"):
                callspec = getattr(self._node, "callspec")
                param_names = callspec.params
                renderable = render_scope(param_names, title="parameters", indent_guides=True)
                table.add_row("Parameters", renderable)

        table.add_section()

        for note in self._stack.notes:
            table.add_row("Note", "[i bright_white]" + note + "[/]")

        console.print(table)
        yield table
