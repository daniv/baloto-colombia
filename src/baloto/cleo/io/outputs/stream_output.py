# Project : baloto-colombia
# File Name : stream_output.py
# Dir Path : src/baloto/cleo/io/outputs
# Created on: 2025–06–08 at 03:05:46.

from __future__ import annotations

import codecs
from functools import cached_property
from typing import Any
from typing import TYPE_CHECKING
from typing import TextIO
from typing import IO

from multipledispatch import dispatch
from rich.console import HighlighterType
from rich.segment import Segment
from rich.style import Style
from rich.text import Text
from rich.text import TextType

from baloto.cleo.io.outputs.output import Output
from baloto.cleo.io.outputs.output import OutputType
from baloto.cleo.io.outputs.output import Verbosity
from baloto.core.richer.logging.console_logger import Log
from baloto.core.richer.console_factory import ConsoleFactory

if TYPE_CHECKING:
    from rich.console import JustifyMethod, RenderableType, ConsoleOptions
    from rich.console import OverflowMethod
    from rich.align import AlignMethod
    from baloto.cleo.io.outputs.section_output import SectionOutput
    from rich.console import Console


__all__ = ("StreamOutput",)


class StreamOutput(Output):

    def __init__(self, console: Console | None = None, verbosity: Verbosity = Verbosity.NORMAL, stderr: bool = False) -> None:
        super().__init__(verbosity=verbosity)
        if console is None:
            if stderr:
                self._console = ConsoleFactory.console_error_output()
            else:
                self._console = ConsoleFactory.console_output()
        else:
            self._console = console

        if type(self).__qualname__ == "BufferedOutput":
            return
        self._log = Log(self._console)

    @cached_property
    def supports_utf8(self) -> bool:
        """
        :return: whether the stream supports the UTF-8 encoding.
        """
        encoding = self._console.encoding

        try:
            return codecs.lookup(encoding).name == "utf-8"
        except LookupError:
            return True

    @property
    def file(self) -> IO[str]:
        return self._console.file

    @property
    def is_terminal(self) -> bool:
        return self._console.is_terminal

    @property
    def log(self) -> Log:
        return self._log

    @dispatch(bool)
    def clear(self, home: bool = True) -> None:
        self._console.clear(home)

    def flush(self) -> None:
        self.file.flush()

    def section(self) -> SectionOutput:
        from baloto.cleo.io.outputs.section_output import SectionOutput

        return SectionOutput(
            self._console,
            self._section_outputs,
            verbosity=self.verbosity
        )

    def line(self, count: int = 1, verbosity: Verbosity = Verbosity.NORMAL) -> None:
        if verbosity.value > self.verbosity:
            return
        self._console.line(count=count)

    def rule(
        self,
        title: TextType = "",
        *,
        characters: str = "=",
        style: str | Style = "rule.line",
        align: AlignMethod = "center",
        verbosity: Verbosity = Verbosity.NORMAL,
    ) -> None:
        if verbosity.value > self.verbosity:
            return
        self._console.rule(title, characters=characters, style=style, align=align)

    def render_str(
        self,
        text: str,
        *,
        style: str | Style = "",
        justify: JustifyMethod | None = None,
        overflow: OverflowMethod | None = None,
        emoji: bool | None = None,
        markup: bool | None = None,
        highlight: bool | None = None,
        highlighter: HighlighterType | None = None,
    ) -> Text:
        return self._console.render_str(
            text,
            style=style,
            justify=justify,
            overflow=overflow,
            emoji=emoji,
            markup=markup,
            highlighter=highlighter,
            highlight=highlight,
        )

    def render_lines(
        self,
        renderable: RenderableType,
        options: ConsoleOptions | None = None,
        *,
        style: Style | None = None,
        pad: bool = True,
        new_lines: bool = False,
    ) -> list[list[Segment]]:
        return self._console.render_lines(
            renderable, options, style=style, pad=pad, new_lines=new_lines
        )

    def _write(
        self,
        *objects: Any,
        sep: str = " ",
        end: str = "\n",
        style: str | Style | None = None,
        justify: JustifyMethod | None = None,
        overflow: OverflowMethod | None = None,
        no_wrap: bool | None = None,
        markup: bool | None = None,
        highlight: bool = True,
        width: int | None = None,
        height: int | None = None,
        crop: bool = True,
        soft_wrap: bool | None = None,
        new_line_start: bool = False,
        verbosity: Verbosity = Verbosity.NORMAL,
        type: OutputType = OutputType.NORMAL,
    ) -> None:
        if type == OutputType.RAW:
            self._console.out(*objects, sep=sep, end=end, style=style, highlight=highlight)
        else:
            self._console.print(
                *objects,
                sep=sep,
                end=end,
                style=style,
                justify=justify,
                overflow=overflow,
                no_wrap=no_wrap,
                markup=markup,
                highlight=highlight,
                width=width,
                height=height,
                crop=crop,
                soft_wrap=soft_wrap,
                new_line_start=new_line_start,
            )

    def prompt(
        self,
        prompt: TextType = "",
        *,
        markup: bool = True,
        password: bool = False,
        stream: TextIO | None = None,
    ) -> str:
        if self._console.is_interactive:
            return self._console.input(prompt, markup=markup, password=password, stream=stream)
        return ""
