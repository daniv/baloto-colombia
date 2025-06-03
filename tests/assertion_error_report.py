# - Project   : baloto-colombia
# - User Naem : solma
# - File Name : assertion_error_report.py
# - Dir Path  : tests
# - Created on: 2025-06-02 at 04:42:47

from __future__ import annotations

import linecache
import traceback as tb
from pathlib import Path
from types import TracebackType
from typing import TYPE_CHECKING, Type, Any

import pytest
from pydantic import validate_call
from rich.rule import Rule
from rich.scope import render_scope
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from rich.traceback import LOCALS_MAX_LENGTH, LOCALS_MAX_STRING
from rich.traceback import Traceback

from baloto.miloto.config.poetry.poetry import BasePoetry

if TYPE_CHECKING:
    from rich.console import Console, ConsoleOptions, RenderResult, group
    from rich.traceback import Stack, Frame, Trace

class AssertionErrorReport:
    """Reports an asssertion error"""

    @validate_call(config=dict(arbitrary_types_allowed=True))
    def __init__(self, exc_type: Type[AssertionError], exc_value: AssertionError, traceback: TracebackType | None, _is_pytest = True):

        self._is_pytest = _is_pytest
        self._trace: Trace = Traceback.extract(exc_type, exc_value, traceback, show_locals=True)
        self._message = str(exc_value).strip()
        self._tb_info: tb.FrameSummary = tb.extract_tb(traceback, limit=1)[-1]

        self._node: pytest.Item | pytest.Collector | None = None
        self._call: pytest.CallInfo[Any] | None = None
        self._report: pytest.CollectReport | pytest.TestReport | None = None

    @property
    def tb_info(self) -> tb.FrameSummary:
        return self._tb_info

    @tb_info.deleter
    def tb_info(self) -> None:
        del self._tb_info

    @property
    def trace(self) -> Trace:
        return self._trace

    @trace.deleter
    def trace(self) -> None:
        del self._trace

    @property
    def node(self) -> pytest.Item | pytest.Collector:
        return self._node

    @node.setter
    def node(self, value: pytest.Item | pytest.Collector) -> None:
        self._node = value

    @node.deleter
    def node(self) -> None:
        del self._node

    @property
    def call(self) -> pytest.CallInfo[Any]:
        return self._call

    @call.setter
    def call(self, value: pytest.CallInfo[Any]) -> None:
        self._call = value

    @call.deleter
    def call(self) -> None:
        del self._call

    @property
    def report(self) -> pytest.CollectReport | pytest.TestReport:
        return self._report

    @report.setter
    def report(self, value: pytest.CollectReport | pytest.TestReport) -> None:
        self._report = value

    @report.deleter
    def report(self) -> None:
        del self._report

    # noinspection PyUnusedLocal
    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        err_message_row = f'"{self._message}"'
        if err_message_row == "":
            err_message_row = "[dim orange3]No error message was given[/]"

        project_dir = BasePoetry.locate(Path.cwd().parent).parent
        lineno = self.tb_info.lineno
        link_path = Path(self.tb_info.filename)
        relative = link_path.relative_to(project_dir)
        filepath_col = f"/{relative.as_posix()}:{lineno}"
        link_name_col = f"[link={link_path}:{lineno}][blue u]Click here for more info[/link]"
        func_row_col = f"[cyan]{self.tb_info.name}()[/]"
        func_comment_col = ""
        if self._is_pytest:
            func_comment_col = "[bright_green]Pytest test[/]"
            func_row_col = f"[bright_green]{self.tb_info.name}[/]"

        code_line = self.tb_info.line
        if code_line:
            try:
                code_lines = linecache.getlines(self.tb_info.filename)
                all_code = "".join(code_lines)
                if all_code:
                    syntax = Syntax(
                            all_code, "python", theme="ansi_dark",
                            line_range=(self.tb_info.lineno - 3, self.tb_info.end_lineno + 2),
                            code_width=88, dedent=True,   line_numbers=True, highlight_lines={self.tb_info.lineno - 1}
                    )
            except Exception as error:
                yield Text.assemble(
                        (f"\n{error}", "traceback.error"),
                )

        @group()
        def render_info(stack: Stack) -> RenderResult:

            frame: Frame = stack.frames[-1]

            table = Table(title="AssertionError Description", highlight=True, show_lines=False, show_edge=True, style="green")
            table.add_column("[bold yellow]Description[/]", style="yellow")
            table.add_column("Value")
            table.add_column("Comments")

            table.add_row("Error Message", err_message_row)
            table.add_row("File Path", filepath_col, link_name_col)
            table.add_row("Function name", func_row_col, func_comment_col)
            table.add_row("Line number", str(frame.lineno))
            if all_code:
                table.add_row("Cause code", code_line)
                table.add_row("Cause code syntax", syntax)

            if frame.locals:
                rendered_locals = render_scope(
                    frame.locals,
                    title="locals",
                    indent_guides=False,
                    max_length=LOCALS_MAX_LENGTH,
                    max_string=LOCALS_MAX_STRING,
                )
                table.add_row("Locals", rendered_locals)
            table.add_section()
            for note in stack.notes:
                table.add_row("Note", note)

            yield table
            yield Rule("[bright_red]Stack Trace", characters="=", style="bright_red dim")


        yield render_info(self.trace.stacks[-1])
        yield Traceback(self.trace, show_locals=True, theme="ansi_dark")
