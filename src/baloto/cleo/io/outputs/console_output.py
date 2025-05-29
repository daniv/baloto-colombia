from __future__ import annotations

import codecs
from functools import cached_property
from typing import Any, Iterable
from typing import TYPE_CHECKING

from baloto.cleo.io.outputs.output import Output, OutputType, Verbosity

if TYPE_CHECKING:
    from baloto.cleo.io.outputs.section_output import SectionOutput
    from rich.console import (
        Console,
        ConsoleOptions,
        RenderableType,
        JustifyMethod,
        OverflowMethod,
        HighlighterType,
    )
    from rich.style import Style
    from rich.align import AlignMethod
    from rich.text import TextType, Text
    from rich.segment import Segment


class ConsoleOutput(Output):
    def __init__(self, console: Console, verbosity: Verbosity = Verbosity.NORMAL) -> None:
        super().__init__(verbosity)
        self.console = console
        self.interactive: bool = console.is_interactive

    @cached_property
    def supports_utf8(self) -> bool:
        """
        :return: whether the stream supports the UTF-8 encoding.
        """
        encoding = self.console.encoding

        try:
            return codecs.lookup(encoding).name == "utf-8"
        except LookupError:
            return True

    def section(self) -> SectionOutput:
        return SectionOutput(self.console, self._section_outputs, verbosity=self.verbosity)

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
        type: OutputType = OutputType.NORMAL,
    ) -> None:
        if type == OutputType.RAW:
            self.console.out(*objects, sep=sep, end=end, style=style, highlight=highlight)
        else:
            self.console.print(
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

    def clear(self, home: bool = True) -> None:
        self.console.clear(home=home)

    def line(self, count: int = 1) -> None:
        self.console.line(count=count)

    def rule(
        self,
        title: TextType = "",
        *,
        characters: str = "─",
        style: str | Style = "rule.line",
        align: AlignMethod = "center",
    ) -> None:
        self.console.rule(title, characters=characters, style=style, align=align)

    def render_lines(
        self,
        renderable: RenderableType,
        options: ConsoleOptions | None = None,
        *,
        style: Style | None = None,
        pad: bool = True,
        new_lines: bool = False,
    ) -> list[list[Segment]]:
        return self.console.render_lines(
            renderable, options, style=style, pad=pad, new_lines=new_lines
        )

    def render(
        self, renderable: RenderableType, options: ConsoleOptions | None = None
    ) -> Iterable[Segment]:
        return self.console.render(renderable, options)

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
        return self.console.render_str(
            text,
            style=style,
            justify=justify,
            overflow=overflow,
            emoji=emoji,
            markup=markup,
            highlighter=highlighter,
            highlight=highlight,
        )
