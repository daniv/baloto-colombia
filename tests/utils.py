from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from rich.console import Console
    from rich.text import TextType
    from rich.style import Style


def print_section_rule(
    console: Console, title: TextType, *, characters: str = "=", style: str | Style = "dim"
) -> None:
    console.rule(title, characters=characters, style=style)
