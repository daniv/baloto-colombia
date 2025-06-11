from __future__ import annotations

import os
import sys
from types import ModuleType
from types import TracebackType
from typing import Iterable
from typing import TYPE_CHECKING
from typing import Type

from rich.columns import Columns
from rich.console import group
from rich.traceback import Traceback

from baloto.core.config.settings import settings

if TYPE_CHECKING:
    from rich.console import ConsoleRenderable, RenderResult
    from rich.traceback import Stack, Frame
    from rich.syntax import Syntax

INDENT = "    "
MIN_WIDTH = 120


class RichTraceback(Traceback):
    @group()
    def _render_stack(self, stack: Stack) -> RenderResult:
        import linecache
        from rich.scope import render_scope
        from rich.text import Text

        # path_highlighter = PathHighlighter()
        theme = self.theme

        def render_locals(f: Frame) -> Iterable[ConsoleRenderable]:
            if f.locals:
                yield render_scope(
                    f.locals,
                    title="locals",
                    indent_guides=self.indent_guides,
                    max_length=self.locals_max_length,
                    max_string=self.locals_max_string,
                )

        exclude_frames: range | None = None
        if self.max_frames != 0:
            exclude_frames = range(
                self.max_frames // 2,
                len(stack.frames) - self.max_frames // 2,
            )

        excluded = False
        for frame_index, frame in enumerate(stack.frames):
            if exclude_frames and frame_index in exclude_frames:
                excluded = True
                continue

            if excluded:
                assert exclude_frames is not None
                yield Text(
                    f"\n... {len(exclude_frames)} frames hidden ...",
                    justify="center",
                    style="traceback.error",
                )
                excluded = False

            first = frame_index == 0
            frame_filename = frame.filename
            suppressed = any(frame_filename.startswith(path) for path in self.suppress)

            if os.path.exists(frame.filename):
                posix = Path(frame.filename).as_posix()
                content = f"{frame.filename}:{frame.lineno} in {frame.name}"
                text = Text.from_markup(
                    f"[blue bold][link={posix}:{frame.lineno}]{content}[/link][/]",
                    style="pygments.text",
                )
            else:
                text = Text.assemble(
                    "in ",
                    (frame.name, "pygments.function"),
                    (":", "pygments.text"),
                    (str(frame.lineno), "pygments.number"),
                    style="pygments.text",
                )
            if not frame.filename.startswith("<") and not first:
                yield ""
            yield text
            if frame.filename.startswith("<"):
                yield from render_locals(frame)
                continue
            if not suppressed:
                try:
                    code_lines = linecache.getlines(frame.filename)
                    code = "".join(code_lines)
                    if not code:
                        continue
                    lexer_name = self._guess_lexer(frame.filename, code)
                    syntax = Syntax(
                        code,
                        lexer_name,
                        theme=theme,
                        line_numbers=True,
                        line_range=(
                            frame.lineno - self.extra_lines,
                            frame.lineno + self.extra_lines,
                        ),
                        highlight_lines={frame.lineno},
                        word_wrap=self.word_wrap,
                        code_width=self.code_width,
                        indent_guides=self.indent_guides,
                        dedent=False,
                    )
                    yield ""
                except Exception as error:
                    yield Text.assemble(
                        (f"\n{error}", "traceback.error"),
                    )
                else:
                    if frame.last_instruction is not None:
                        from rich.traceback import _iter_syntax_lines

                        start, end = frame.last_instruction
                        for line1, column1, column2 in _iter_syntax_lines(start, end):
                            try:
                                if column1 == 0:
                                    line = code_lines[line1 - 1]
                                    column1 = len(line) - len(line.lstrip())
                                if column2 == -1:
                                    column2 = len(code_lines[line1 - 1])
                            except IndexError:
                                continue

                            syntax.stylize_range(
                                style="traceback.error_range",
                                start=(line1, column1),
                                end=(line1, column2),
                            )
                    yield (
                        Columns(
                            [
                                syntax,
                                *render_locals(frame),
                            ],
                            padding=1,
                        )
                        if frame.locals
                        else syntax
                    )


def from_exception(
    exc_value: BaseException,
    *,
    exc_type: Type[BaseException] | None = None,
    tb: TracebackType | None = None,
    width: int = settings.tracebacks.width,
    code_width: int = settings.tracebacks.code_width,
    extra_lines: int = settings.tracebacks.extra_lines,
    word_wrap: bool = settings.tracebacks.word_wrap,
    show_locals: bool = settings.tracebacks.show_locals,
    locals_max_length: int = settings.tracebacks.locals_max_length,
    locals_max_string: int = settings.tracebacks.locals_max_string,
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

    # from rich.padding import Padding
    # return Padding(tb, (0, 0, 0, 4))
    return tb


def traceback() -> ConsoleRenderable:
    exc_type, exc_value, tb = sys.exc_info()
    if exc_type is None or exc_value is None or traceback is None:
        raise ValueError("Value for 'trace' required if not called in except: block")
    return from_exception(exc_value, exc_type=exc_type, tb=tb)
