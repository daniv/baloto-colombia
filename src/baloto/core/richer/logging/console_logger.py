# Project : baloto-colombia
# File Name : log.py
# Dir Path : src/baloto/cleo/rich/logging
# Created on: 2025–06–07 at 00:01:37.

from __future__ import annotations

from enum import StrEnum
from typing import Any
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rich.console import Console
    from rich.style import Style
    from rich.console import JustifyMethod


class Log2:
    def __init__(self, filename):
        self.filename = filename
        self.fp = None

    def logging(self, text):
        self.fp.write(text + "\n")

    def __enter__(self):
        print("__enter__")
        self.fp = open(self.filename, "a+")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("__exit__")
        self.fp.close()


class MessagePrefixEnum(StrEnum):
    PREFIX_SQUARE = " ▪ "
    PREFIX_BULLET = " • "
    PREFIX_DASH = " - "
    PREFIX_BIG_SQARE = " ■ "
    PREFIX_BIG_CIRCLE = " ⬤ "
    BLACK_CIRCLE = " ● "
    LARGE_CIRCLE = " ○ "
    MEDIUM_SMALL_WHITE_CIRCLE = " ⚬ "
    CIRCLED_BULLET = " ⦿ "
    CIRCLED_WHITE_BULLET = " ⦾ "
    NARY_BULLET = " ⨀ "


# with Log(r"C:\Users\SharpEl\Desktop\myfile.txt") as logfile:
#     print("Main")
#     logfile.logging("Test1")
#     logfile.logging("Test2")


class Log:
    def __init__(self, console: Console):
        self._console = console
        self._log_locals: bool = False

    @property
    def log_locals(self) -> bool:
        return self._log_locals

    @log_locals.setter
    def log_locals(self, value: bool) -> None:
        self._log_locals = value

    def debug(
        self,
        *objects: Any,
        sep: str = " ",
        end: str = "\n",
        style: str | Style | None = None,
        justify: JustifyMethod | None = None,
        emoji: bool | None = None,
        markup: bool | None = None,
        highlight: bool | None = None,
        log_locals: bool = False,
    ): ...

    def info(
        self,
        *objects: Any,
        sep: str = " ",
        end: str = "\n",
        style: str | Style | None = None,
        justify: JustifyMethod | None = None,
        emoji: bool | None = None,
        markup: bool | None = None,
        highlight: bool | None = None,
        log_locals: bool = False,
    ): ...

    def warning(
        self,
        *objects: Any,
        sep: str = " ",
        end: str = "\n",
        style: str | Style | None = None,
        justify: JustifyMethod | None = None,
        emoji: bool | None = None,
        markup: bool | None = None,
        highlight: bool | None = None,
        log_locals: bool = False,
    ): ...

    def error(
        self,
        *objects: Any,
        sep: str = " ",
        end: str = "\n",
        style: str | Style | None = None,
        justify: JustifyMethod | None = None,
        emoji: bool | None = None,
        markup: bool | None = None,
        highlight: bool | None = None,
        log_locals: bool = False,
    ): ...

    def fatal(
        self,
        *objects: Any,
        sep: str = " ",
        end: str = "\n",
        style: str | Style | None = None,
        justify: JustifyMethod | None = None,
        emoji: bool | None = None,
        markup: bool | None = None,
        highlight: bool | None = None,
        log_locals: bool = False,
    ): ...

    def _log(
        self,
        *objects: Any,
        sep: str = " ",
        end: str = "\n",
        style: str | Style | None = None,
        justify: JustifyMethod | None = None,
        emoji: bool | None = None,
        markup: bool | None = None,
        highlight: bool | None = None,
        log_locals: bool = False,
        stack_offset: int = 1,
    ) -> None:
        self._console.log(
            *objects,
            sep=sep,
            end=end,
            style=style,
            justify=justify,
            emoji=emoji,
            markup=markup,
            highlight=highlight,
            log_locals=log_locals,
            _stack_offset=stack_offset,
        )
