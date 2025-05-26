from __future__ import annotations

import math
from io import StringIO
from typing import Any
from typing import TYPE_CHECKING

from rich.control import CONTROL_CODES_FORMAT
from rich.control import Control
from rich.segment import ControlType

from baloto.core.cleo.io.outputs.console_output import ConsoleOutput
from baloto.core.cleo.io.outputs.output import Verbosity

if TYPE_CHECKING:
    from rich.console import Console, ConsoleDimensions
    from rich.style import Style
    from rich.console import JustifyMethod
    from rich.console import OverflowMethod


class SectionOutput(ConsoleOutput):
    def __init__(
        self,
        console: Console,
        sections: list[SectionOutput],
        verbosity: Verbosity = Verbosity.NORMAL,
    ) -> None:
        super().__init__(console, verbosity)

        self._content: list[str] = []
        self._lines = 0
        sections.insert(0, self)
        self._sections = sections
        self._terminal_size: ConsoleDimensions = console.size

    @property
    def content(self) -> str:
        return "".join(self._content)

    @property
    def lines(self) -> int:
        return self._lines

    def do_clear(self, lines: int | None = None) -> None:
        if not self._content:
            return

        if lines:
            del self._content[-lines * 2 :]
        else:
            lines = self._lines
            self._content = []

        self._lines -= lines

        func = CONTROL_CODES_FORMAT[ControlType.ERASE_IN_LINE]
        try:
            CONTROL_CODES_FORMAT[ControlType.ERASE_IN_LINE] = lambda: "\x1b[0J"
            self.console.control(
                # Move cursor up n lines
                Control((ControlType.CURSOR_UP, lines)),
                # Erase to end of screen
                Control(ControlType.ERASE_IN_LINE),
            )
        finally:
            CONTROL_CODES_FORMAT[ControlType.ERASE_IN_LINE] = func

    def _pop_stream_content_until_current_section(self, lines_to_clear_count: int = 0) -> None:
        erased_content = []

        for section in self._sections:
            if section is self:
                break

            lines_to_clear_count += section.lines
            erased_content.append(section.content)

        if lines_to_clear_count > 0:
            raise NotImplementedError()
        # return "".join(reversed(erased_content))

    def add_content(self, *objects: Any) -> None:
        for line_content in objects:
            no_format = len(self.remove_format(line_content).replace("\t", " " * 8))
            self._lines += (
                math.ceil(no_format / self.console.width)
                or 1
            )
            self._content.append(line_content)
            self._content.append("\n")

    def overwrite(self, message: str) -> None:
        self.clear()
        self.write(message)

    def _write(
        self,
        *objects: Any,
        sep: str = " ",
        end: str = "",
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
    ) -> None:
        erased_content = self._pop_stream_content_until_current_section()

        self.add_content(*objects)
        self.console.print(*objects)
