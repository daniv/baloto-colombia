from __future__ import annotations

from io import StringIO
from typing import TYPE_CHECKING
from typing import IO

from baloto.cleo.io.outputs.console_output import ConsoleOutput
from baloto.cleo.io.outputs.output import Verbosity

if TYPE_CHECKING:
    from rich.console import Console


class BufferedOutput(ConsoleOutput):
    def __init__(self, console: Console, verbosity: Verbosity = Verbosity.NORMAL) -> None:

        self.console.file = StringIO()
        self._buffer: IO[str] = self.console.file
        super().__init__(console, verbosity)

    def fetch(self) -> str:
        """
        Empties the buffer and returns its content.
        """
        assert isinstance(self._buffer, StringIO)
        content = self._buffer.getvalue()
        self._buffer = StringIO()

        return content

    def clear(self, home: bool = True) -> None:
        """
        Empties the buffer.
        """
        self._buffer = StringIO()
