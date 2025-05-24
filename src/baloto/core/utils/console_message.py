from __future__ import annotations

import dataclasses


@dataclasses.dataclass(frozen=False, slots=True, repr=False, unsafe_hash=True)
class ConsoleMessage:
    """
    Representation of a console message, providing utilities for formatting text
    with tags, indentation, and sections.

    The ConsoleMessage class is designed to represent text messages that might be
    displayed in a console or terminal output. It provides features for managing
    formatted text, such as stripping tags, wrapping text with specific tags,
    indenting, and creating structured message sections.
    """

    text: str
    debug: bool = False

    @property
    def stripped(self) -> str:
        from baloto.core.cleo.formatters.formatter import Formatter

        return Formatter.strip_styles(self.text)

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
    ) -> ConsoleMessage:
        if not self.text:
            return self

        if self.text:
            section = [f"[b]{title}:[/]"] if title else []
            section.extend(self.text.splitlines())
            self.text = f"\n{indent}".join(section).strip()

        return self
