from __future__ import annotations

import re
from collections.abc import Sequence
from functools import cached_property
from typing import TYPE_CHECKING, Iterator, Iterable, Pattern

from rich.color import ColorSystem
from rich.style import Style
from rich.text import Text

from baloto.cleo.exceptions.errors import CleoKeyError

if TYPE_CHECKING:
    from rich.console import OverflowMethod, JustifyMethod, ConsoleRenderable
    from rich.emoji import EmojiVariant
    from rich.style import StyleType
    from rich.theme import Theme
    from rich.text import GetStyleCallable


# https://github.com/paul-ollis/pytest-richer/blob/main/src/pytest_richer/theming.py


## https://github.com/paul-ollis/pytest-richer/blob/main/src/pytest_richer/theming.py


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

        self._theme: Theme | None = None
        self._styles: dict[str, Style] = {}
        self._text: Text = Text("")

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

    def set_text(self, text: str, style: StyleType = "") -> None:
        self._text = Text(text, style=style)

    def highlight_words(
        self,
        words: Iterable[str],
        style: str | Style,
        *,
        case_sensitive: bool = True,
    ) -> int:
        return self._text.highlight_words(words, style, case_sensitive=case_sensitive)

    def highlight_regex(
        self,
        re_highlight: Pattern[str] | str,
        style: GetStyleCallable | StyleType | None = None,
        *,
        style_prefix: str = "",
    ) -> int:
        return self._text.highlight_regex(re_highlight, style, style_prefix=style_prefix)

    def set_from_ansi(
        self,
        text: str,
        *,
        style: str | Style = "",
        justify: JustifyMethod | None = None,
        overflow: OverflowMethod | None = None,
        no_wrap: bool | None = None,
        end: str = "\n",
        tab_size: int | None = 8,
    ) -> Text:
        self._text = Text.from_ansi(
            text, style=style, justify=justify, overflow=overflow, no_wrap=no_wrap, end=end, tab_size=tab_size
        )
        return self._text

    def to_ansi(
        self,
        *,
        color_system: ColorSystem | None = ColorSystem.TRUECOLOR,
        legacy_windows: bool = False,
    ) -> str:
        style = Style()
        if self._text.style or self._text.style == "":
            if isinstance(self._text.style, Style):
                style = self._text.style
            if isinstance(self._text.style, str):
                style = Style.parse(self._text.style)

        return style.render(self._text.plain, color_system=color_system, legacy_windows=legacy_windows)


    def set_from_markup(
        self,
        text: str,
        *,
        style: str | Style = "",
        emoji: bool = True,
        emoji_variant: EmojiVariant | None = None,
        justify: JustifyMethod | None = None,
        overflow: OverflowMethod | None = None,
        end: str = "\n",
    ) -> Text:
        self._text = Text.from_markup(
            text, style=style, justify=justify, overflow=overflow, emoji=emoji, end=end, emoji_variant=emoji_variant
        )
        return self._text

    def set_style(self, name: str, style: StyleType) -> None:
        self._styles[name] = style

    def has_style(self, name: str) -> bool:
        return name in self._styles

    def style(self, name: str) -> Style:
        if not self.has_style(name):
            raise CleoKeyError(f'Undefined style: "{name}"')

        return self._styles[name]

    def styles_names(self, rich_styles: bool = False) -> Iterator[str]:
        if rich_styles:
            return iter(self.ansi_color_names)
        return iter(self._styles.keys())

    def render_styles(
        self,
        styles: dict[str, Style],
    ) -> Iterator[str]:
        lines: list[str] = []

        if not styles:
            styles = self.formatter_styles()

        largest = len(max(list(styles.keys()), key=len))
        for n, s in styles.items():
            fmt = f"{{:>{largest}}} ->  {s.render(self._text.plain)}"
            lines.append(fmt.format(n))

        return iter(lines)

    def create_theme(self, styles: dict[str, Style] | None) -> Theme:
        from rich.theme import Theme

        if styles is None:
            styles = self._styles
        return Theme(styles)

    @cached_property
    def ansi_color_names(self) -> Sequence[str]:
        from rich.color import ANSI_COLOR_NAMES

        return list(ANSI_COLOR_NAMES.keys())

    @cached_property
    def rich_default_styles(self) -> dict[str, Style]:
        from rich.default_styles import DEFAULT_STYLES
        styles_dict: dict[str, Style] = DEFAULT_STYLES.copy()
        return styles_dict

    @cached_property
    def rich_ansi_styles(self) -> dict[str, Style]:
        styles_dict = {name: Style.parse(name) for name in self.ansi_color_names}
        return styles_dict

    def formatter_styles(self) -> dict[str, Style]:
        return self._styles.copy()

    def render_rich_colors(self) -> ConsoleRenderable:
        from rich.table import Table
        from rich.color import ANSI_COLOR_NAMES

        color_names = list(ANSI_COLOR_NAMES.keys())

        color_table = Table(
                title="Rich colors",
                expand=False,
                show_header=True,
                show_edge=False,
                pad_edge=False,
                highlight=True
        )
        color_table.add_column(Text("Color Name", style="bright_blue bold"), no_wrap=True, justify="right", style="bold gray69")
        color_table.add_column(Text("Demonstration", style="bright_blue bold") )

        plain = self._text.plain
        for n in color_names:
            color_table.add_row(n, Text(plain, style=n))

        return color_table

    # --- Service Functions

    @staticmethod
    def strip_styles(text: str) -> str:
        return Formatter._escape.sub("", text)


