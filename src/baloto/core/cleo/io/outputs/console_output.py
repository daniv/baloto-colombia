from __future__ import annotations

import codecs
import io
import locale
import os
import sys

from typing import TYPE_CHECKING
from typing import TextIO
from typing import IO
from typing import Any
from typing import cast

from baloto.core.cleo.io.outputs.output import Output
from baloto.core.cleo.io.outputs.output import Verbosity


if TYPE_CHECKING:
    from baloto.core.cleo.io.outputs.section_output import SectionOutput
    from rich.console import Console
    from rich.style import Style
    from rich.console import JustifyMethod
    from rich.console import OverflowMethod


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

    def _write(
        self,
        *objects: Any,
        sep: str = " ",
        end: str = "\n",
        style: str | Style | None = None,
        justify: JustifyMethod | None = None,
        overflow: OverflowMethod | None = None,
        no_wrap: bool | None = None,
        markup: bool | None = None,
        highlight: bool = True,
        width: int | None = None,
        height: int | None = None,
        crop: bool = True,
        soft_wrap: bool | None = None,
        new_line_start: bool = False,
    ) -> None:
        self._console.print(
            *objects,
            sep=sep,
            end=end,
            style=style,
            justify=justify,
            overflow=overflow,
            no_wrap=no_wrap,
            markup=markup,
            highlight=highlight,
            width=width,
            height=height,
            crop=crop,
            soft_wrap=soft_wrap,
            new_line_start=new_line_start,
        )
