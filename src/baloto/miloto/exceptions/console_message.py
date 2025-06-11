# Project : baloto-colombia
# File Name : console_message.py
# Dir Path : src/baloto/miloto/exceptions
# Created on: 2025–06–09 at 02:55:33.

from __future__ import annotations

import dataclasses
from typing import Annotated
from typing import TYPE_CHECKING

from pydantic import BaseModel
from pydantic import StringConstraints

if TYPE_CHECKING:
    pass

__all__ = ("ConsoleMessage", )


# noinspection PyTypeHints
class ConsoleMessage:
    text: str

    def wrap(self, tag: str) -> ConsoleMessage:
        if self.text:
            self.text = f"[{tag}]{self.text}[/]"
        return self

    def indent(self, indent: str) -> ConsoleMessage:
        if self.text:
            self.text = f"\n{indent}".join(self.text.splitlines()).strip()
            self.text = f"{indent}{self.text}"
        return self

    def make_section(
        self,
        title: str,
        indent: str = "",
    ) -> None:
        if not self.text:
            return

        if self.text:
            section = [f"[b]{title}:[/]"] if title else []
            section.extend(self.text.splitlines())
            self.text = f"\n{indent}".join(section).strip()
