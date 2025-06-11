# Project : baloto-colombia
# File Name : stream_input.py
# Dir Path : src/baloto/cleo/io/inputs
# Created on: 2025–06–08 at 04:22:51.

from __future__ import annotations

from typing import IO
from typing import TYPE_CHECKING
from typing import TextIO

from rich.text import TextType

from baloto.cleo.io.inputs.input import Input
from baloto.cleo.io.inputs.string_input import StringInput

if TYPE_CHECKING:
    from rich.console import Console

__all__ = ("StreamInput",)


class StreamInput(StringInput):

    def __init__(self, bufffer: IO[str]) -> None:
        super().__init__("")
        self._buffer = bufffer




