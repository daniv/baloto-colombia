from __future__ import annotations

import re

# https://github.com/paul-ollis/pytest-richer/blob/main/src/pytest_richer/theming.py


from rich.style import Style
from rich.syntax import TokenType
from rich.theme import Theme

from baloto.core.cleo.exceptions import CleoValueError

## https://github.com/paul-ollis/pytest-richer/blob/main/src/pytest_richer/theming.py

# ANSI_LIGHT: dict[TokenType, Style] = {
#     Token: Style(),
#     Whitespace: Style(color="white"),
#     Comment: Style(dim=True),
#     Comment.Preproc: Style(color="cyan"),
#     Keyword: Style(color="blue"),
#     Keyword.Type: Style(color="cyan"),
#     Operator.Word: Style(color="magenta"),
#     Name.Builtin: Style(color="cyan"),
#     Name.Function: Style(color="green"),
#     Name.Namespace: Style(color="cyan", underline=True),
#     Name.Class: Style(color="green", underline=True),
#     Name.Exception: Style(color="cyan"),
#     Name.Decorator: Style(color="magenta", bold=True),
#     Name.Variable: Style(color="red"),
#     Name.Constant: Style(color="red"),
#     Name.Attribute: Style(color="cyan"),
#     Name.Tag: Style(color="bright_blue"),
#     String: Style(color="yellow"),
#     Number: Style(color="blue"),
#     Generic.Deleted: Style(color="bright_red"),
#     Generic.Inserted: Style(color="green"),
#     Generic.Heading: Style(bold=True),
#     Generic.Subheading: Style(color="magenta", bold=True),
#     Generic.Prompt: Style(bold=True),
#     Generic.Error: Style(color="bright_red"),
#     Error: Style(color="red", underline=True),
# }
#
# ANSI_DARK: Dict[TokenType, Style] = {
#     Token: Style(),
#     Whitespace: Style(color="bright_black"),
#     Comment: Style(dim=True),
#     Comment.Preproc: Style(color="bright_cyan"),
#     Keyword: Style(color="bright_blue"),
#     Keyword.Type: Style(color="bright_cyan"),
#     Operator.Word: Style(color="bright_magenta"),
#     Name.Builtin: Style(color="bright_cyan"),
#     Name.Function: Style(color="bright_green"),
#     Name.Namespace: Style(color="bright_cyan", underline=True),
#     Name.Class: Style(color="bright_green", underline=True),
#     Name.Exception: Style(color="bright_cyan"),
#     Name.Decorator: Style(color="bright_magenta", bold=True),
#     Name.Variable: Style(color="bright_red"),
#     Name.Constant: Style(color="bright_red"),
#     Name.Attribute: Style(color="bright_cyan"),
#     Name.Tag: Style(color="bright_blue"),
#     String: Style(color="yellow"),
#     Number: Style(color="bright_blue"),
#     Generic.Deleted: Style(color="bright_red"),
#     Generic.Inserted: Style(color="bright_green"),
#     Generic.Heading: Style(bold=True),
#     Generic.Subheading: Style(color="bright_magenta", bold=True),
#     Generic.Prompt: Style(bold=True),
#     Generic.Error: Style(color="bright_red"),
#     Error: Style(color="red", underline=True),
# }



class Formatter:
    _escape = re.compile(r"(\\*)(\[[a-z#/@][^[]*?])")

    def __init__(self, styles: dict[str, Style] | None = None) -> None:
        self._styles: dict[str, Style] = {}

        self.set_style("error", Style(color="red", bold=True))
        self.set_style("warning", Style(color="yellow"))
        self.set_style("info", Style(color="deep_sky_blue1"))
        self.set_style("debug", Style(color="default", dim=True))
        self.set_style("success", Style(color="green", bold=True))
        self.set_style("comment", Style(dim=True))
        self.set_style("c1", Style(color="cyan", italic=True))

        # ------------------------

        self.set_style("name.variable", Style(color="bright_red"))
        self.set_style("name.constant", Style(color="bright_red"))
        self.set_style("name.attribute", Style(color="bright_cyan"))
        self.set_style("name.function", Style(color="bright_green"))
        self.set_style("name.class", Style(color="bright_green", underline=True))
        self.set_style("name.exception",Style(color="bright_cyan"))

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

    def create_theme(self) -> Theme:
        return Theme(self._styles)

    @staticmethod
    def strip_styles(text: str) -> str:
        return Formatter._escape.sub("", text)
