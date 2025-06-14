# Project : baloto-colombia
# File Name : section_message.py
# Dir Path : src/baloto/cleo/rich
# Created on: 2025–06–09 at 18:53:01.
from __future__ import annotations

from typing import List
from typing import TYPE_CHECKING

from rich.text import Text

if TYPE_CHECKING:
    from rich.console import Console
    from rich.console import ConsoleOptions, RenderResult


__all__ = ("SectionMessages",)


class SectionMessages:

    def __init__(self, title: str, indent_size: int = 2, use_enum: bool = False) -> None:
        """Creates a section message with title and bulleted messages

        :param title: The section title
        :param indent_size: the indent size from the left
        :param use_enum: instead use emumeration bulleting
        """
        self.title = title
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
        yield Text(f"{self.title}:", style="bold")

        for i, message in enumerate(self.messages, start=1):
            if self.use_enum:
                y = Text.from_markup(message)
                yield console.render_str(self.indent_size * " " + f"{i}. ").append_text(y)
            else:
                y = Text.from_markup(message)
                yield console.render_str(self.indent_size * " " + "- ").append_text(y)
