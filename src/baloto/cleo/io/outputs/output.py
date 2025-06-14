# Project : baloto-colombia
# File Name : output.py
# Dir Path : src/baloto/cleo/io/outputs
# Created on: 2025–06–08 at 01:58:38.

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from enum import IntEnum
from typing import Any
from typing import TYPE_CHECKING

from rich.style import Style


if TYPE_CHECKING:
    from rich.console import JustifyMethod
    from rich.console import OverflowMethod
    from baloto.cleo.io.outputs.section_output import SectionOutput

__all__ = ("Verbosity", "OutputType", "Output")


class Verbosity(IntEnum):
    QUIET = -1  # --quiet
    NORMAL = 0
    VERBOSE = 1  # -v
    VERY_VERBOSE = 2  # -vv
    DEBUG = 3  # -vvv


class OutputType(IntEnum):
    NORMAL = 1
    RAW = 2


class Output(ABC):
    def __init__(
        self,
        verbosity: Verbosity = Verbosity.NORMAL,
    ) -> None:
        self._verbosity: Verbosity = verbosity
        self._section_outputs: list[SectionOutput] = []

    @property
    def verbosity(self) -> Verbosity:
        return self._verbosity

    def set_verbosity(self, verbosity: Verbosity) -> None:
        self._verbosity = verbosity

    def is_quiet(self) -> bool:
        return self.verbosity is Verbosity.QUIET

    def is_verbose(self) -> bool:
        return self.verbosity.value >= Verbosity.VERBOSE.value

    def is_very_verbose(self) -> bool:
        return self.verbosity.value >= Verbosity.VERY_VERBOSE.value

    def is_debug(self) -> bool:
        return self.verbosity is Verbosity.DEBUG

    @property
    def supports_utf8(self) -> bool:
        """
        Returns whether the stream supports the UTF-8 encoding.
        """
        return True

    def write(
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
        verbosity: Verbosity = Verbosity.NORMAL,
        type: OutputType = OutputType.NORMAL,
    ) -> None:
        if verbosity.value > self.verbosity:
            return

        self._write(
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
            type=type,
        )

    @abstractmethod
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
        raise NotImplementedError("[c1]_write[/] is an abstract method")

    @abstractmethod
    def flush(self) -> None:
        raise NotImplementedError("[c1]flush[/] is an abstract method")

    @abstractmethod
    def section(self) -> SectionOutput:
        raise NotImplementedError("[c1]section[/] is an abstract method")
