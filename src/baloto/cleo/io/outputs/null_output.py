# Project : baloto-colombia
# File Name : null_output.py
# Dir Path : src/baloto/cleo/io/outputs
# Created on: 2025–06–08 at 12:47:28.

from __future__ import annotations

from typing import Any
from typing import TYPE_CHECKING

from rich.style import Style

from baloto.cleo.io.outputs.output import Verbosity
from baloto.cleo.io.outputs.output import OutputType
from baloto.cleo.io.outputs.stream_output import StreamOutput
from baloto.cleo.rich.console_factory import ConsoleFactory

if TYPE_CHECKING:
    from rich.console import JustifyMethod
    from rich.console import OverflowMethod

__all__ = ("NullOutput",)


class NullOutput(StreamOutput):
    def __init__(self, verbosity: Verbosity = Verbosity.NORMAL) -> None:
        super().__init__(verbosity=verbosity)

        self._console = ConsoleFactory.null_output()

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
        type: OutputType = OutputType.NORMAL,
    ) -> None:
        pass

    @property
    def verbosity(self) -> Verbosity:
        return Verbosity.QUIET

    def set_verbosity(self, verbosity: Verbosity) -> None:
        pass

    def is_quiet(self) -> bool:
        return True

    def is_verbose(self) -> bool:
        return False

    def is_very_verbose(self) -> bool:
        return False

    def is_debug(self) -> bool:
        return False
