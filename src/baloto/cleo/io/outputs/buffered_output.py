# Project : baloto-colombia
# File Name : buffered_output.py
# Dir Path : src/baloto/cleo/io/outputs
# Created on: 2025–06–08 at 02:27:22.

from __future__ import annotations

from io import StringIO
from typing import TYPE_CHECKING

from multipledispatch import dispatch

from baloto.cleo.io.outputs.output import Verbosity
from baloto.cleo.io.outputs.stream_output import StreamOutput
from baloto.cleo.rich.console_factory import ConsoleFactory

if TYPE_CHECKING:
    pass

__all__ = ("BufferedOutput",)


class BufferedOutput(StreamOutput):
    def __init__(
        self, verbosity: Verbosity = Verbosity.NORMAL, file: StringIO | None = None
    ) -> None:
        super().__init__(verbosity=verbosity)

        self._buffer = file or StringIO()
        self._console = ConsoleFactory.buffered_output(verbosity, file=self._buffer)

    def fetch(self) -> str:
        """
        Empties the buffer and returns its content.
        """
        content = self._buffer.getvalue()
        self._buffer = StringIO()

        return content

    @property
    def supports_utf8(self) -> bool:
        return True

    @dispatch()
    def clear(self) -> None:
        self._console.file = StringIO()
