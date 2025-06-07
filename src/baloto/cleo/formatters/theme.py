# Project : baloto-colombia
# File Name : theme.py
# Dir Path : src/baloto/cleo/formatters
# Created on: 2025–06–06 at 17:28:52.

from __future__ import annotations

from typing import TYPE_CHECKING

from pygments.token import Comment, Error, Generic, Keyword, Name, Number, Operator, String, Token, Whitespace
from pygments.token import Text as TextToken
from rich.color import Color
from rich.highlighter import ReprHighlighter
from rich.style import Style
from rich.syntax import ANSISyntaxTheme
from rich.theme import Theme


if TYPE_CHECKING:
    from rich.syntax import TokenType

__all__ = ("MilotoHighlighter", "MilotoTheme")

DARK: dict[TokenType, Style] = {
    Token: Style(),
    Whitespace: Style(color="bright_black"),
    Comment: Style(color=Color.parse("#7A7E85")),
    Comment.Preproc: Style(color="bright_cyan"),
    Keyword: Style(color="bright_blue"),
    Keyword.Type: Style(color="bright_cyan"),
    Operator.Word: Style(color="bright_magenta"),
    Name.Builtin: Style(color="bright_cyan"),
    Name.Function: Style(color=Color.parse("#56A8F5")),
    Name.Namespace: Style(color="bright_cyan", underline=True),
    Name.Class: Style(color="bright_green", underline=True),
    Name.Exception: Style(color=Color.parse("#8888C6")),
    Name.Decorator: Style(color="bright_magenta", bold=True),
    Name.Variable: Style(color="bright_red"),
    Name.Constant: Style(color="bright_red"),
    Name.Attribute: Style(color="bright_cyan"),
    Name.Tag: Style(color="bright_blue"),
    String: Style(color=Color.parse("#6AAB73")),
    Number: Style(color=Color.parse("#2AACB8")),
    Generic.Deleted: Style(color="bright_red"),
    Generic.Inserted: Style(color="bright_green"),
    Generic.Heading: Style(bold=True),
    Generic.Subheading: Style(color="bright_magenta", bold=False),
    Generic.Prompt: Style(bold=True),
    Generic.Error: Style(color="bright_red"),
    Error: Style(color="red", underline=False),
}


class MilotoTheme(Theme):

    ini_file = "static/styles/miloto.ini"

    def __init__(self) -> None:
        from baloto.miloto.config.poetry.poetry import locate

        filename = locate(self.ini_file)
        theme_from_file = Theme.read(str(filename))
        syntax_theme = ANSISyntaxTheme(DARK)

        token_style = syntax_theme.get_style_for_token

        miloto_styles = {
            "pretty": token_style(TextToken),
            "pygments.text": token_style(Token),
            "pygments.string": token_style(String),
            "pygments.function": token_style(Name.Function),
            "pygments.number": token_style(Number),
            "pygments.comment": token_style(Comment),
            "repr.str": token_style(String),
            "repr.exception": token_style(Name.Exception),
        }
        miloto_styles.update(theme_from_file.styles)
        super().__init__(miloto_styles, True)

    @classmethod
    def save_theme(cls, theme: Theme) -> None:
        from baloto.miloto.config.poetry.poetry import locate

        filename = locate(cls.ini_file)
        with open(filename, "wt") as write_theme:
            write_theme.write(theme.config)


class MilotoHighlighter(ReprHighlighter):
    def __init__(self):
        self.highlights.append(
            r"\b(?P<exception>AssertionError|KeyError|AttributeError|Exception|RuntimeError|IOError|SyntaxError|FileNotFoundError|FileExistsError|TypeError|NotImplementedError|ValueError|BaseException|ModuleNotFoundError|KeyboardInterrupt|IndexError)\b"
        )

