# Project : baloto-colombia
# File Name : buffered_output.py
# Dir Path : src/baloto/cleo/io/outputs
# Created on: 2025–06–08 at 02:27:22.

from __future__ import annotations

from io import StringIO
from typing import TYPE_CHECKING
from typing import cast

from multipledispatch import dispatch

from baloto.cleo.io.outputs.output import Verbosity
from baloto.cleo.io.outputs.stream_output import StreamOutput
from baloto.core.richer.console_factory import ConsoleFactory
from baloto.core.richer.logging.console_logger import Log

if TYPE_CHECKING:
    pass

__all__ = ("BufferedOutput",)


class BufferedOutput(StreamOutput):
    def __init__(self, verbosity: Verbosity = Verbosity.NORMAL) -> None:
        console = ConsoleFactory.buffered_output(StringIO())
        super().__init__(console, verbosity=verbosity)
        self._log = None

    def fetch(self) -> str:
        """
        Empties the buffer and returns its content.
        """
        content = cast(StringIO, self._console.file).getvalue()
        self.clear()

        return content

    @property
    def supports_utf8(self) -> bool:
        return True

    @dispatch()
    def clear(self) -> None:
        self._console.file = StringIO()

    @property
    def log(self) -> Log:
        raise TypeError("Buffered output does not log.")
