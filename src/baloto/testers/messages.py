# Project : baloto-colombia
# File Name : messages.py
# Dir Path : src/baloto/core/rich/testers
# Created on: 2025–06–12 at 00:17:03.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import Literal
from typing import Self
from typing import TYPE_CHECKING

import rich.repr
from rich.table import Column
from rich.table import Table
from rich.text import Text

from baloto.core.richer import MessagePrefixEnum

if TYPE_CHECKING:
    from rich.console import Console
    from rich.console import ConsoleOptions
    from rich.console import RenderResult

__all__ = ("HookMessage", "RenderType")


@dataclass
class KeyValue:
    key: str
    value: Any
    key_color: str
    value_color: str


RenderType = Literal["plain", "markup"]


@rich.repr.auto
class HookMessage:
    def __init__(
        self, hookname: str, *, prefix: MessagePrefixEnum = MessagePrefixEnum.PREFIX_SQUARE
    ) -> None:
        self.hookname = hookname
        self.prefix = prefix  # .value()
        self.info: str = ""
        self._info_markup: str | None = None
        self.key_values: list[KeyValue] = []

    # @validate_call
    def add_info(self, info: str, render_as: Literal["plain", "markup"] = "plain") -> Self:

        from rich.ansi import re_ansi

        if re_ansi.findall(info):
            text = Text.from_ansi(info)
            self.info = text.plain
            self._info_markup = text.markup

        if self._info_markup is None:
            text = Text.from_markup(info)
            self._info_markup = text.markup
            self.info = text.plain

        if render_as == "plain":
            self._info_markup = None

        return self

    def add_key_value(
        self,
        key: str,
        value: str,
        *,
        key_color: str = "pytest.keyname",
        value_color: str = "white",
        escape_markup: bool = True,
    ) -> Self:
        value = value.replace("[", "\\[") if escape_markup else value
        kv = KeyValue(key=key, value=value, key_color=key_color, value_color=value_color)
        self.key_values.append(kv)
        return self

    def set_prefix(self, prefix: MessagePrefixEnum) -> Self:
        self.prefix = prefix  # .value()
        return self

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        table = Table.grid(
            Column(
                "prefix", width=3, style="pytest.hook", max_width=3, min_width=3, justify="center"
            ),
            Column("hook", width=6, justify="left", max_width=6, min_width=6),
            Column("hookname", justify="left", width=30, min_width=30, max_width=30),
            Column("info"),
            expand=False,
        )

        kv_table = None
        table.add_row(
            self.prefix,
            "[pytest.hook]hook[/]:",
            f"[pytest.hookname]{self.hookname}[/]",
            f"[white]{self.info}[/]",
        )
        if self.key_values:
            kv_table = Table.grid(
                Column("prefix", width=5, max_width=5, min_width=5, justify="center"),
                Column("key", justify="left"),
                Column("value", justify="left"),
            )
            for item in self.key_values:
                markup = (
                    item.value
                    if item.value_color == "repr"
                    else f"[{item.value_color}]{item.value}[/]"
                )
                kv_table.add_row(
                    "   - ",
                    console.render_str(item.key, style=item.key_color),
                    # f"[{item.key_color}]{item.key}[/]: ",
                    f"{markup}",
                )
            kv_table.add_row("   - ", "num", "7")
            kv_table.add_row("   - ", "bool", "True")
            kv_table.add_row(
                "   - ",
                "link",
                "C:/Users/solma/PycharmProjects/baloto-colombia/src/baloto/core/rich/logging.py:34",
            )

        yield table
        if kv_table:
            yield kv_table
            yield ""
