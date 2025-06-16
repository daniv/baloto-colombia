# Project : baloto-colombia
# File Name : section_output.py
# Dir Path : src/baloto/cleo/io/inputs
# Created on: 2025–06–12 at 20:04:10.

from __future__ import annotations

import math
from typing import Any
from typing import TYPE_CHECKING

from rich.text import Text

from baloto.cleo.io.outputs.output import OutputType
from baloto.cleo.io.outputs.output import Verbosity
from baloto.cleo.io.outputs.stream_output import StreamOutput

if TYPE_CHECKING:
    from rich.console import Console
    from baloto.core.richer.logging.console_logger import Log
    from rich.console import JustifyMethod
    from rich.console import OverflowMethod
    from rich.style import Style

__all__ = ("SectionOutput", )

# https://gist.github.com/ConnerWill/d4b6c776b509add763e17f9f113fd25b

class SectionOutput(StreamOutput):
    def __init__(self, console: Console, sections: list[SectionOutput], verbosity: Verbosity = Verbosity.NORMAL) -> None:
        super().__init__(console, verbosity)

        self._content: list[str] = []
        self._lines = 0
        sections.insert(0, self)
        self._sections = sections

    @property
    def content(self) -> str:
        return "".join(self._content)

    @property
    def lines(self) -> int:
        return self._lines

    @property
    def log(self) -> Log:
        raise TypeError("Section output does not log.")

    def add_content(self, content: str) -> None:
        for line_content in content.split("\n"):
            plain = Text.from_ansi(line_content).plain
            plain = plain.replace("\t", " " * 8)
            len_line = len(plain)
            self._lines += (math.ceil(len_line / self._console.width) or 1)
            self._content.append(line_content)
            self._content.append("\n")

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
        erased_content = self._pop_stream_content_until_current_section()
        self._console.control()
        self.add_content(message)

        super()._write(message)
        super()._write(erased_content, end="")