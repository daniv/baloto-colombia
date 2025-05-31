from __future__ import annotations

import re
from collections.abc import Sequence
from functools import cached_property
from typing import Any, TYPE_CHECKING, Iterator

from rich.text import Text

from baloto.cleo.exceptions.errors import CleoValueError

if TYPE_CHECKING:
    from rich.console import ConsoleRenderable, OverflowMethod, JustifyMethod
    from rich.emoji import EmojiVariant
    from rich.style import Style
    from rich.theme import Theme

# https://github.com/paul-ollis/pytest-richer/blob/main/src/pytest_richer/theming.py


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
        from rich.style import Style

        self._theme: Theme | None = None
        self._styles: dict[str, Style] = {}
        self._text: Text | None = None

        self.set_style("error", Style(color="red", bold=True))
        self.set_style("warning", Style(color="yellow"))
        self.set_style("info", Style(color="deep_sky_blue1"))
        self.set_style("debug", Style(color="default", dim=True))
        self.set_style("success", Style(color="bright_green", bold=True))
        self.set_style("comment", Style(dim=True))
        self.set_style("c1", Style(color="cyan", italic=True))

        # ------------------------

        self.set_style("name.variable", Style(color="bright_red"))
        self.set_style("name.constant", Style(color="bright_red"))
        self.set_style("name.attribute", Style(color="bright_cyan"))
        self.set_style("name.function", Style(color="bright_green"))
        self.set_style("name.class", Style(color="bright_green", underline=True))
        self.set_style("name.exception", Style(color="bright_cyan"))

        # --------- cleo specifics

        self.set_style("switch", Style(color="bright_green", italic=True))
        self.set_style("command", Style(color="bright_magenta", bold=True))
        self.set_style("alias", Style(color="bright_magenta", italic=True, bold=True))
        self.set_style("prog", Style(color="medium_orchid3", bold=True))
        self.set_style("opt", Style(color="bright_cyan", bold=True))
        self.set_style("arg", Style(color="bright_cyan", bold=True))

        for name, style in (styles or {}).items():
            self.set_style(name, style)

    @property
    def default_theme(self) -> Theme:
        if self._theme is None:
            self._theme = self.create_theme(None)
        return self._theme

    @property
    def text(self) -> Text:
        return self._text

    def from_ansi(
        self,
        text: str,
        *,
        style: str | Style = "",
        justify: JustifyMethod | None = None,
        overflow: OverflowMethod | None = None,
        no_wrap: bool | None = None,
        end: str = "\n",
        tab_size: int | None = 8,
    ) -> None:
        self._text = Text.from_ansi(
            text, style=style, justify=justify, overflow=overflow, no_wrap=no_wrap, end=end, tab_size=tab_size
        )

    def from_markup(
        self,
        text: str,
        *,
        style: str | Style = "",
        emoji: bool = True,
        emoji_variant: EmojiVariant | None = None,
        justify: JustifyMethod | None = None,
        overflow: OverflowMethod | None = None,
        end: str = "\n",
    ) -> None:
        self._text = Text.from_markup(
            text, style=style, justify=justify, overflow=overflow, emoji=emoji, end=end, emoji_variant=emoji_variant
        )

    def set_style(self, name: str, style: Style) -> None:
        self._styles[name] = style

    def has_style(self, name: str) -> bool:
        return name in self._styles

    def style(self, name: str) -> Style:
        if not self.has_style(name):
            raise CleoValueError(f'Undefined style: "{name}"')

        return self._styles[name]

    def styles_names(self) -> Iterator[str]:
        return iter(self._styles.keys())

    def create_theme(self, styles: dict[str, Style] | None) -> Theme:
        from rich.theme import Theme

        if styles is None:
            styles = self._styles
        return Theme(styles)

    @staticmethod
    def raw_output(*objects: Any, sep: str = " ") -> str:
        return sep.join(str(_object) for _object in objects)

    def strip(self, text: str) -> str:
        return self.strip_styles(text)

    def styles_renderables(self, styles_names: Sequence[str] | None = None) -> ConsoleRenderable:
        from rich.table import Table

        if styles_names is None:
            styles_names = list(self.styles_names())

        # color_table = Table(
        #         box=None,
        #         expand=False,
        #         show_header=False,
        #         show_edge=False,
        #         pad_edge=False,
        # )
        lorem = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. 1234567890  !¡¿'=)(/&"
        table = Table.grid(padding=1, pad_edge=True)
        table.title = "Formatter styles"
        table.add_column("Stle Name", no_wrap=True, justify="center", style="bold red")
        table.add_column("Demonstration")
        t = table.row_count

        map(lambda n: table.add_row(n, Text(lorem, style=n)), styles_names)
        t = table.row_count
        i = 0

        return Table

    def rich_renderables(self) -> ConsoleRenderable:
        return self.styles_renderables(self.ansi_color_names)

    @cached_property
    def ansi_color_names(self) -> Sequence[str]:
        from rich.color import ANSI_COLOR_NAMES

        return list(ANSI_COLOR_NAMES.keys())

    @staticmethod
    def strip_styles(text: str) -> str:
        return Formatter._escape.sub("", text)
