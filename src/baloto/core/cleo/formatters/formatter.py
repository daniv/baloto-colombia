from __future__ import annotations

import re
from typing import Iterable, TYPE_CHECKING

from rich.style import Style
from rich.theme import Theme

from baloto.core.cleo.exceptions import CleoValueError

if TYPE_CHECKING:
    from rich.segment import Segment


class Formatter:
    _escape = re.compile(r"(\\*)(\[[a-z#/@][^[]*?])")

    def __init__(self, styles: dict[str, Style] | None = None):
        self._styles: dict[str, Style] = {}

        self.set_style("error", Style(color="red", bold=True))
        self.set_style("warning", Style(color="yellow"))
        self.set_style("info", Style(color="deep_sky_blue1"))
        self.set_style("debug", Style(color="default", dim=True))
        self.set_style("success", Style(color="green", bold=True))
        self.set_style("comment", Style(color="green", italic=True))
        self.set_style("c1", Style(color="cyan", italic=True))

        for name, style in (styles or {}).items():
            self.set_style(name, style)

    def set_style(self, name: str, style: Style) -> None:
        self._styles[name] = style

    def has_style(self, name: str) -> bool:
        return name in self._styles

    def style(self, name: str) -> Style:
        if not self.has_style(name):
            raise CleoValueError(f'Undefined style: "{name}"')

        return self._styles[name]

    def create_theme(self):
        return Theme(self._styles)

    @staticmethod
    def strip_ansi(value: str) -> str:
        from click._compat import strip_ansi

        return strip_ansi(value)

    @staticmethod
    def strip_styles(text: str) -> str:
        return Formatter._escape.sub("", text)
