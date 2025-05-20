from __future__ import annotations

import codecs
import io
import locale
import os
import sys

from typing import TYPE_CHECKING
from typing import TextIO, IO
from typing import cast

from baloto.core.cleo.io.outputs.output import Output
from baloto.core.cleo.io.outputs.output import Verbosity


if TYPE_CHECKING:
    from baloto.core.cleo.io.outputs.section_output import SectionOutput
    from rich.console import Console


class ConsoleOutput(Output):
    def __init__(self, console: Console, verbosity: Verbosity = Verbosity.NORMAL) -> None:
        super().__init__(verbosity)

        self._console = console
        self._supports_utf8 = self._get_utf8_support_info()

    @property
    def console(self) -> Console:
        return self._console

    @property
    def file(self) -> IO[str]:
        return self._console.file

    @property
    def is_error(self) -> bool:
        return self._console.stderr

    @property
    def width(self) -> int:
        return self._console.width

    @property
    def height(self) -> int:
        return self._console.height

    @property
    def supports_utf8(self) -> bool:
        return self._supports_utf8

    def _get_utf8_support_info(self) -> bool:
        """
        :return: whether the stream supports the UTF-8 encoding.
        """
        encoding = self._console.encoding

        try:
            return codecs.lookup(encoding).name == "utf-8"
        except LookupError:
            return True

    def section(self) -> SectionOutput:
        pass

    def _write(self, message: str, new_line: bool = False) -> None:
        pass
