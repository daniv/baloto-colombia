# Project : baloto-colombia
# File Name : eerrr.py
# Dir Path : tests
# Created on: 2025–06–09 at 20:43:13.

from __future__ import annotations

from typing import List
from typing import TYPE_CHECKING

from rich.text import Text

if TYPE_CHECKING:
    from rich.console import Console, ConsoleOptions, RenderResult

class SectionMessagese:

    def __init__(self, section: str, indent_size: int = 2, use_enum: bool = False) -> None:
        self.section = section
        self._messages: List[str] = []
        self.indent_size = indent_size
        self.use_enum = use_enum

    @property
    def messages(self):
        return self._messages

    @messages.setter
    def messages(self, messages: List[str]) -> None:
        self._messages = messages

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        yield Text(f"{self.section}:", style="bold")

        for i, message in enumerate(self.messages, start=1):
            if self.use_enum:
                y = Text.from_markup(message)
                yield console.render_str(self.indent_size * " " + f"{i}. ").append_text(y)
            else:
                y = Text.from_markup(message)
                yield console.render_str(self.indent_size * " " + "- ").append_text(y)


if __name__ == '__main__':
    from baloto.cleo.rich.console_factory import ConsoleFactory

    c = ConsoleFactory.console_output()
    sm = SectionMessagese("Section", use_enum=True, indent_size=8)
    sm.messages = []
    c.print(sm)
