from __future__ import annotations

import codecs
import dataclasses
import sys
from functools import cached_property
from typing import Any, Iterable, Mapping
from typing import TYPE_CHECKING


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


def render(self, renderable: RenderableType, options: ConsoleOptions | None = None) -> Iterable[Segment]:
    return self.console.render(renderable, options)


def _log(
    self,
    *objects: Any,
    sep: str = " ",
    end: str = "\n",
    style: str | Style | None = None,
    justify: JustifyMethod | None = None,
    emoji: bool | None = None,
    markup: bool | None = None,
    highlight: bool | None = None,
    log_locals: bool = False,
    stack_offset: int = 4,
) -> None:
    self.console.log(
        *objects,
        sep=sep,
        end=end,
        style=style,
        justify=justify,
        markup=markup,
        highlight=highlight,
        log_locals=log_locals,
        emoji=emoji,
        _stack_offset=stack_offset,
    )
