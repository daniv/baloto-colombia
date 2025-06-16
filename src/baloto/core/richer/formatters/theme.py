# Project : baloto-colombia
# File Name : theme.py
# Dir Path : src/baloto/cleo/formatters
# Created on: 2025–06–06 at 17:28:52.

### EXCELENT COLOR SCHEME https://ghostty.org/docs/vt/csi/el

from __future__ import annotations

from typing import TYPE_CHECKING

from pygments.token import Comment
from pygments.token import Error
from pygments.token import Generic
from pygments.token import Keyword
from pygments.token import Name
from pygments.token import Number
from pygments.token import Operator
from pygments.token import String
from pygments.token import Text as TextToken
from pygments.token import Token
from pygments.token import Whitespace
from rich.color import Color
from rich.style import Style
from rich.syntax import ANSISyntaxTheme
from rich.theme import Theme


if TYPE_CHECKING:
    from rich.syntax import TokenType

DARK: dict[TokenType, Style] = {
    Token: Style(),
    Whitespace: Style(color="bright_black"),
    Comment: Style(color=Color.parse("#7A7E85")),
    Comment.Preproc: Style(color="yellow"),
    # Keyword: Style(color="bright_blue"),
    Keyword: Style(color=Color.parse("#CF8E6D")),
    Keyword.Type: Style(color="yellow"),
    # Keyword.Argument: Style(color=Color.parse("#AA4926")), # NOT FOUND
    Operator.Sign: Style(color="violet", underline=True),
    # Operator.Sign: Style(color="violet", underline=True),
    Operator.Word: Style(color="bright_magenta"),
    Name.Builtin: Style(color="yellow"),
    Name.Function: Style(color=Color.parse("#56A8F5")),
    Name.Namespace: Style(color="yellow", underline=True),
    Name.Class: Style(color=Color.parse("#CF8E6D")),
    Name.Exception: Style(color=Color.parse("#8888C6")),
    Name.Decorator: Style(color=Color.parse("#B3AE60"), bold=True),
    Name.Variable: Style(color="bright_red"),
    Name.Constant: Style(color="bright_red"),
    Name.Attribute: Style(color="yellow"),
    Name.Definition: Style(color=Color.parse("#B200B2")),  # neet to validate __init__
    Name.Tag: Style(color="bright_blue", underline=True),
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


class RichSyntaxTheme(ANSISyntaxTheme):
    def __init__(self) -> None:
        super().__init__(DARK)


class RichTheme(Theme):

    ini_file = "static/styles/baloto.ini"

    def __init__(self) -> None:

        syntax_theme = RichSyntaxTheme()
        from baloto.core.richer.settings import locate

        filename = locate(self.ini_file)
        theme_from_file = Theme.read(str(filename))
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

        # "repr.indent": token_style(Comment) + Style(dim=True),
        # "repr.str": token_style(String),
        # "repr.brace": token_style(TextToken) + Style(bold=True),
        # "repr.number": token_style(Number),
        # "repr.bool_true": token_style(Keyword.Constant),
        # "repr.bool_false": token_style(Keyword.Constant),
        # "repr.none": token_style(Keyword.Constant),
        # "scope.border": token_style(String.Delimiter),
        # "scope.equals": token_style(Operator),
        # "scope.key": token_style(Name),
        # "scope.key.special": token_style(Name.Constant) + Style(dim=True),

    @classmethod
    def save_theme(cls, theme: Theme) -> None:
        from baloto.core.richer.settings import locate

        filename = locate(cls.ini_file)
        with open(filename, "wt") as write_theme:
            write_theme.write(theme.config)
