# - Project   : baloto-colombia
# - User Naem : solma
# - File Name : assert_report.py
# - Dir Path  : tests
# - Created on: 2025-06-02 at 00:54:42

from __future__ import annotations

import inspect
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from traceback import extract_tb, walk_tb
from types import TracebackType, CodeType
from typing import TYPE_CHECKING, Type, Any, Iterable, Sequence

import pytest
from click import style
from rich.columns import Columns
from rich.console import group
from rich.style import Style
from rich.syntax import Syntax
from rich.table import Table
from rich.traceback import Trace
from rich.traceback import Traceback, LOCALS_MAX_LENGTH, LOCALS_MAX_STRING, Stack, Frame

from baloto.cleo.formatters.formatter import Formatter
from baloto.cleo.utils import safe_str
from rich import pretty

if TYPE_CHECKING:
    from rich.console import Console, ConsoleOptions, RenderResult
    from traceback import StackSummary, FrameSummary
    from _pytest import _code as pytestcode
    from _pytest._code import code as pytestcode_code

    # from _pytest._code import ExceptionInfo, Traceback, TracebackEntry
    # from _pytest._code.code import ExceptionChainRepr, ExceptionRepr, ExceptionInfo, ReprEntryNative, ReprExceptionInfo, ReprEntry
    # from _pytest._code.code import ExceptionChainRepr


class AssertionReportException(Exception):
    pass


# class AssertionReportExceptionGroup(ExceptionGroup):
#     def derive(self, excs):
#         return AssertionReportExceptionGroup(self.message, excs)

@dataclass
class ReportTrace:
    stack: ReportStack


@dataclass
class ReportFrame(Frame):
    instruction: tuple[int, int] | None = None

@dataclass
class ReportStack(Stack):
    frame: ReportFrame | None = None


# @dataclass
# class NodeInfo:
#     nodeid: str
#     nodename: str
#     nodepath: Path
#     linkpath: str
#     linkname: str
#     own_markers: list[pytest.Mark] = field(default_factory=list)
#     funcargs: dict[str, object] = field(default_factory=dict)
#
#     def __post_init__(self):
#         i = 0

@dataclass
class ReportInfo:
    headline: str
    when: str
    filename_posix: str
    duration_ms: float
    user_properties: Iterable[tuple[str, object]] | None = None



@dataclass
class PytestInfo:
    # node: NodeInfo
    report: ReportInfo
    trace: ReportTrace

@dataclass
class ExceptionInteractInfo:
    crash_message: str
    crash_lineno: int
    crash_path: str
    nodeid: str
    nodename: str
    nodepath: Path
    headline: str
    when: str
    filename_posix: str
    duration: float
    source: list[str] = field(default_factory=list)
    statement: list[str] = field(default_factory=list)
    fullsource: list[str] = field(default_factory=list)
    raw: CodeType = None
    linkpath: str = ""
    linkname: str = ""
    own_markers: list[pytest.Mark] = field(default_factory=list)
    funcargs: dict[str, object] = field(default_factory=dict)
    frame: ReportFrame | None = None
    stack: ReportStack | None = None
    user_properties: Iterable[tuple[str, object]] | None = None
    trace: ReportTrace | None = None

    def __post_init__(self):
        self.duration = self.duration * 1_000
        self.linkpath = f"[link={self.nodepath}:{self.crash_lineno + 1}][blue u]Click here for more info[/link][/]"
        self.linkname = f"{self.nodepath.name}:{self.crash_lineno + 1}"



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
        if call.excinfo.type is None or call.excinfo.value is None or call.excinfo.tb is None:
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
        # self.pytest_info: PytestInfo | None = None
        self.raise_exec = raise_exceptions
        self.show_locals: bool = node.config.option.showlocals
        self._fulltrace = node.config.option.fulltrace
        self._tbstyle: str = node.config.option.tbstyle
        self._verbose_level: int = node.config.option.verbose


        # call_info = CallInfo(
        #     crash_message=self.longrepr.reprcrash.message.strip(),
        #     crash_lineno=self.longrepr.reprcrash.lineno,
        #     crash_path=self.longrepr.reprcrash.path
        # )
        # node_info = NodeInfo(
        #     # nodeid=node.nodeid,
        #     # nodename=node.name,
        #     # nodepath=node.path,
        #     own_markers=node.own_markers,
        #     funcargs=getattr(node, "funcargs", {}),
        #     # linkpath= f"[link={node.path}:{node.location[1] + 1}][blue u]Click here for more info[/link][/]",
        #     # linkname=f"{node.path.name}:{node.location[1] + 1}"
        # )

        self._info = ExceptionInteractInfo(
            crash_message=report.longrepr.reprcrash.message.strip(),
            crash_lineno=report.longrepr.reprcrash.lineno,
            crash_path=report.longrepr.reprcrash.path,
            nodeid=node.nodeid,
            nodename=node.name,
            nodepath=node.path,
            headline=report.head_line,
            when=report.when,
            filename_posix=report.fspath,
            duration=report.duration,
            user_properties=report.user_properties
        )
        # linkpath=f"[link={node.path}:{node.location[1] + 1}][blue u]Click here for more info[/link][/]",
        # linkname=f"{node.path.name}:{node.location[1] + 1}"

        # report_info = ReportInfo(
        #     headline=report.head_line,
        #     when=report.when,
        #     filename_posix=report.fspath,
        #     duration_ms=report.duration * 1000,
        #     user_properties=report.user_properties
        # )
        err_msg = "Could not locate the matching pytest FrameSummary"
        frame_summary = self._frame_summary(self._info.crash_lineno, self._info.crash_path)
        if frame_summary:

            predicate = lambda x: x.lineno == self._info.crash_lineno - 1 and x.path == node.path
            traceback_entry = next(filter(predicate, reversed(call.excinfo.traceback)), None)

            # source = traceback_entry.source
            #
            # code = "".join(code_lines)

            if traceback_entry:
                import linecache
                fullsource = linecache.getlines(str(node.path))

                mapto = lambda x: "\n" if x == "" else x + "\n"

                source = list(map(mapto, traceback_entry.source.lines))
                statement = list(map(mapto, traceback_entry.statement.lines))

                self._info.source = source
                self._info.statement = statement
                # self._info.source = traceback_entry.source
                # self._info.statement = traceback_entry.statement
                self._info.fullsource = fullsource
                self._info.raw = traceback_entry.frame.code.raw

            helper = self._frame_summary(self._info.crash_lineno, self._info.crash_path)
            self._info.trace = self.extract(helper, show_locals=True)

                # self.pytest_info = PytestInfo(
                #     call=call_info, node=node_info, report=report_info, trace=trace_info
                # )
        elif raise_exceptions:
            raise AssertionReportException("Could not locate the matching pytest FrameSummary")
        else:
            warnings.warn(err_msg, category=RuntimeWarning, stacklevel=2)
            self._can_render_report = False
            return

    @property
    def traceback(self) -> TracebackType:
        """A python TracebackType instance from call.excinfo.tb

        :return: a python TracebackType instance
        """
        return self._call.excinfo.tb

    @property
    def exc_type(self) -> Type[AssertionError | BaseException]:
        """The python traceback type instance from call.excinfo.type

        :return: a python Type[BaseException] instance
        """
        return self._call.excinfo.type

    @property
    def exc_value(self) -> BaseException | AssertionError:
        """The python exception, in this case an AssertionError from call.excinfo.value

        :return: a python AssertionError instance
        """
        return self._call.excinfo.value

    @property
    def verbosity_level(self) -> int:
        return 0

    @property
    def longrepr(self) -> pytestcode_code.ExceptionChainRepr | None:
        return self._report.longrepr

    @property
    def report_status(self) -> bool:
        return self._can_render_report

    def _frame_summary(self, lineno: int, path: str) -> FrameSummary | None:
        """Locates the first matching pytest FrameSummary based on lineno and path or None if not found
        Use the native traceback python library to extract the StackSummary instance
        Return a StackSummary object representing a list of pre-processed entries from traceback.

        :param lineno: the crash line nomber
        :param path: the crash line nomber
        :return: an instance of FrameSummary based on predicate
        """
        predicate = lambda x: x.lineno == lineno and x.filename == path
        stack_summary = extract_tb(self._call.excinfo.tb)
        return next(filter(predicate, reversed(stack_summary)), None)

    # def _traceback_entry(self, lineno: int, path: Path) -> pytestcode.TracebackEntry | None:
    #     predicate = lambda x: x.lineno == lineno and x.path == path
    #     return next(filter(predicate, reversed(self._call.excinfo.traceback)), None)
    #

    def pytest_internalerror(self, excrepr: pytestcode_code.ExceptionRepr) -> None: ...

    def render(self, console):
        # in group
        formatter = Formatter()
        from rich import box

        print("")

        table = Table(
            title="AssertionError Report",
            caption="Triggered by [bright_blue]pytest_exception_interact[/] pytest hook",
            box=box.HORIZONTALS,
            collapse_padding=False,
            expand=True,
            show_header=True,
            style="grey42",
            # row_styles="",
            header_style="light_goldenrod2",
            title_style="b",
            caption_style="gray46",
            title_justify="center",
            caption_justify="right",
            highlight=True
        )

        table.add_column("Topic", min_width=15, style="b i", max_width=20, justify="left")
        table.add_column("Value")
        table.add_column("Comments", width=20, style="dim")

        table.add_row("EXCEPTION INFORMATION", style=Style(color="bright_cyan", italic=False))
        formatter.set_text(self._info.crash_message)
        formatter.highlight_words(["AssertionError:"], style="medium_purple1")
        formatter.highlight_words(["Expected:", "but:"], style="i")

        table.add_row("Error Message", formatter.text.markup, style="none")

        table.add_row("At line", str(self._info.crash_lineno))
        table.add_row("On test file", "/" + self._info.filename_posix)
        table.add_row("In test", self._info.nodename)

        stack = self._info.trace.stack
        frame = stack.frame

        code = "".join(self._info.statement)
        code = "".join(self._info.fullsource)
        syntax = Syntax(
            code, "python", theme="ansi_dark", line_numbers=True, code_width=100, indent_guides=True,
            line_range=(
                frame.instruction[0],
                frame.instruction[1],
            ),
            highlight_lines={frame.instruction[0]}
        )

        # syntax = Syntax(
        #     code, "python", theme="ansi_dark", code_width=100, indent_guides=True, dedent=True
        # )

        table.add_row("Cause code", syntax)
        table.add_section()

        table.add_row("TEST INFORMATION", style=Style(color="bright_cyan", italic=False))

        table.add_row("Test Name", "[bright_green]" + self._info.headline + "[/]")
        # TODO: Neet to look at headlines
        # if self._testname != self._nodeid:
        #    table.add_row("Test ID", self._nodeid)

        value = self._info.linkname
        comment = self._info.linkpath
        table.add_row("Location", "[gray70]" + value + "[/]", comment)

        table.add_row("When in test", "[bright_blue b]" + self._info.when + "[/]")

        table.add_row("Test Duration", str(self._info.duration), "in milliseconds")

        console.line(3)
        #console.print(table)

        table.add_section()

        table.add_row("self.pytest_info.node.nodename", self._info.nodename)

        table.add_row("self.pytest_info.node.nodeid", self._info.nodeid)
        console.line(3)
        #console.print(table)



        error_syntax = Syntax(
            code, "python", theme="ansi_dark", line_numbers=True, code_width=100, indent_guides=True,
            line_range=(
                frame.instruction[0] - 3,
                frame.instruction[1] + 1,
            ),
            highlight_lines={frame.instruction[0]}
        )

        table.add_row("Test Duration", error_syntax)
        # syntax = Syntax(self._info.statement, "python", theme="ansi_dark", code_width=80, indent_guides=False)


        # table.add_row("self.pytest_info.node.nodeid", self.pytest_info.node.funcargs)
        # table.add_row("self.pytest_info.node.own_markers", self.pytest_info.node.own_markers)

        # table.add_row("Function name", "[bright_blue]" + self._funcname + "[/]")
        # table.add_row("Line no", str(self._lineno))

        # table.add_section()
        # for note in self._exc_value.__notes__:
        #     table.add_row("Note", "[i bright_white]" + note + "[/]")
        return table

    def extract(
        self,
        helper: FrameSummary,
        *,
        show_locals: bool = False,
        locals_max_length: int = LOCALS_MAX_LENGTH,
        locals_max_string: int = LOCALS_MAX_STRING,
        locals_hide_dunder: bool = True,
        locals_hide_sunder: bool = False,
    ) -> ReportTrace:

        trace: ReportTrace | None = None
        stack: ReportStack | None = None
        is_cause = False
        notes: list[str] = getattr(self.exc_value, "__notes__", None) or []

        stack = ReportStack(
            exc_type=safe_str(self.exc_type.__name__),
            exc_value=safe_str(self.exc_value),
            is_cause=is_cause,
            notes=notes,
        )

        def get_locals(
            iter_locals: Iterable[tuple[str, object]],
        ) -> Iterable[tuple[str, object]]:
            """Extract locals from an iterator of key pairs."""
            if not (locals_hide_dunder or locals_hide_sunder):
                yield from iter_locals
                return
            for key, value in iter_locals:
                if locals_hide_dunder and key.startswith("__"):
                    continue
                if locals_hide_sunder and key.startswith("_"):
                    continue
                yield key, value

        for frame_summary, line_no in walk_tb(self.traceback):
            filename = frame_summary.f_code.co_filename
            if line_no != self.longrepr.reprcrash.lineno and filename != self.longrepr.reprcrash.path:
                continue

            f_code = frame_summary.f_code
            instruction: tuple[int, int] | None = None
            if helper.lineno is not None and helper.end_lineno is not None:
                instruction = ( helper.lineno, helper.end_lineno, )

            frame = ReportFrame(
                filename=filename or "?",
                lineno=line_no,
                name=frame_summary.f_code.co_name,
                locals=(
                    {
                        key: pretty.traverse(
                            value,
                            max_length=locals_max_length,
                            max_string=locals_max_string,
                        )
                        for key, value in get_locals(frame_summary.f_locals.items())
                        if not (inspect.isfunction(value) or inspect.isclass(value))
                    }
                    if show_locals
                    else None
                ),
                instruction=instruction,
            )
            stack.frame = frame
            trace = ReportTrace(stack=stack)

            return trace

        if trace is None:
            raise AssertionReportException("Could not locate the python FrameSummary item on Traceback")

    # noinspection PyUnusedLocal
    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        import linecache
        from rich.text import Text

        err_message_row = f'"{self._message}"'
        if err_message_row == "":
            err_message_row = "[dim orange3]No error message was given[/]"

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
                        all_code,
                        "python",
                        theme="ansi_dark",
                        line_range=(self.tb_info.lineno - 3, self.tb_info.end_lineno + 2),
                        code_width=88,
                        dedent=True,
                        line_numbers=True,
                        highlight_lines={self.tb_info.lineno - 1},
                    )
            except Exception as error:
                yield Text.assemble(
                    (f"\n{error}", "traceback.error"),
                )

        @group()
        def render_info(stack: Stack) -> RenderResult:
            from rich.scope import render_scope
            from rich.traceback import LOCALS_MAX_LENGTH, LOCALS_MAX_STRING

            frame: Frame = stack.frames[-1]

            table = Table(
                title="AssertionError Description", highlight=True, show_lines=False, show_edge=True, style="green"
            )
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

        yield render_info(self.trace.stacks[-1])
