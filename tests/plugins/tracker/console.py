# — Project : baloto-colombia
# — File Name : console.py
# — Dir Path : tests/plugins/error_reporter
# — Created on: 2025–06–05 at 02:12:03.
"""
PYTEST_DONT_REWRITE
"""

from __future__ import annotations

import sys
from textwrap import indent, wrap
from typing import TYPE_CHECKING

from baloto.cleo.utils import safe_str

if TYPE_CHECKING:
    from rich.console import Console, AlignMethod
    from rich.text import Text
    from rich.style import Style

__all__ = ("print_hook_info", "print_key", "print_value", "print_separator", "print_key_value")


INDENT = "    "
MIN_WIDTH = 120
sys.dont_write_bytecode = True


def _format_hook_info(
    name: str,
    *,
    info: str = "",
    prefix: str = "",
) -> str:
    name = name.ljust(28, " ")
    if info:
        info = info.replace("[", "\\[")
        return f"{prefix}[hook]hook[/]: [hookname]{name}[/] {info}"
    else:
        return f"{prefix}[hook]hook[/]: [hookname]{name}[/]"


def print_separator(
    console: Console,
    title: str | Text = "",
    *,
    characters: str = "─",
    style: str | Style = "rule.line",
    end: str = "\n",
    align: AlignMethod = "center",
    width: int | None = None,
) -> None:
    from rich.rule import Rule

    output = Rule(title, characters=characters, style=style, end=end, align=align)
    if width:
        console.print(output, width=width, new_line_start=True)
    else:
        console.print(output, new_line_start=True)


def _format_key(key: str, *, prefix: str = "", color: str = "white") -> str:
    return f"{prefix}[{color}]{key}[/]:"


def print_key(
    console: Console,
    key: str,
    *,
    prefix: str = "",
    color: str = "white",
) -> None:
    output = _format_key(key, prefix=prefix, color=color)
    console.print(output, new_line_start=True)


def _format_value(
    value: str,
    *,
    prefix: str = "",
    color: str = "white",
    wrap_text: bool = True,
    width: int = 80,
) -> str:
    if wrap_text:
        value = "\n".join(
            wrap(
                value,
                initial_indent=prefix,
                subsequent_indent=prefix,
                width=width - len(prefix) - 8,
            )
        )
    else:
        value = indent(value, prefix=prefix)
    value = value.replace("[", "\\[")
    if color == "repr":
        return value
    return f"[{color}]{value}[/]"


def print_value(
    console: Console,
    value: str,
    *,
    prefix: str = "",
    color: str = "white",
    wrap_text: bool = True,
) -> None:
    output = _format_value(
        value, prefix=prefix, color=color, wrap_text=wrap_text, width=console.width
    )
    console.print(output, new_line_start=True)


def _format_key_value(
    key: str,
    value: str,
    *,
    prefix: str = "",
    key_color="keyname",
    value_color="white",
) -> str:
    value = value.replace("[", "\\[")
    value_and_color = str(value) if value_color == "repr" else f"[{value_color}]{value}[/]"
    return f"{prefix}[{key_color}]{key}[/]: {value_and_color}"


def print_key_value(
    console: Console,
    key: str,
    value: str,
    *,
    prefix: str = "",
    key_color: str = "keyname",
) -> None:

    output = f"{prefix}[{key_color}]{key}[/]: {safe_str(value)}"
    console.print(output, overflow="ellipsis")
