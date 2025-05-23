from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING
from typing import Any


if TYPE_CHECKING:
    from baloto.core.cleo.io.outputs.section_output import SectionOutput
    from rich.style import Style
    from rich.console import JustifyMethod
    from rich.console import OverflowMethod


class Verbosity(Enum):
    QUIET = 16
    NORMAL = 32
    VERBOSE = 64  # -v
    VERY_VERBOSE = 128  # -vv
    DEBUG = 256  # -vvv


class Type(Enum):
    NORMAL = 1
    RAW = 2
    PLAIN = 4


class Output(ABC):
    def __init__(self, verbosity: Verbosity = Verbosity.NORMAL) -> None:
        self._verbosity: Verbosity = verbosity
        self._section_outputs: list[SectionOutput] = []

    @property
    def verbosity(self) -> Verbosity:
        return self._verbosity

    @property
    @abstractmethod
    def supports_utf8(self) -> bool:
        """
        Returns whether the stream supports the UTF-8 encoding.
        """

    def set_verbosity(self, verbosity: Verbosity) -> None:
        self._verbosity = verbosity

    def is_quiet(self) -> bool:
        return self._verbosity is Verbosity.QUIET

    def is_verbose(self) -> bool:
        return self._verbosity.value >= Verbosity.VERBOSE.value

    def is_very_verbose(self) -> bool:
        return self._verbosity.value >= Verbosity.VERY_VERBOSE.value

    def is_debug(self) -> bool:
        return self._verbosity is Verbosity.DEBUG

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
        type: Type = Type.NORMAL,
    ) -> None:
        if verbosity.value > self.verbosity.value:
            return

        # for message in objects:
        #     if type is Type.PLAIN:
        #         message = strip_tags(message)
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
        )

    def flush(self) -> None:
        pass

    @abstractmethod
    def section(self) -> SectionOutput:
        raise NotImplementedError

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
    ) -> None:
        raise NotImplementedError
