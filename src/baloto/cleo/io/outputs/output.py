from __future__ import annotations

from abc import ABC, abstractmethod
from enum import IntEnum
from typing import Any
from typing import TYPE_CHECKING

from baloto.cleo.rich.factory.console_factory import ConsoleFactory
from baloto.utils import is_pydevd_mode

if TYPE_CHECKING:
    from baloto.cleo.formatters.formatter import Formatter
    from baloto.cleo.io.outputs.section_output import SectionOutput
    from rich.style import Style
    from rich.console import JustifyMethod
    from rich.console import OverflowMethod
    from rich.console import Console


class Verbosity(IntEnum):
    QUIET = 16  # --quiet
    NORMAL = 32
    VERBOSE = 64  # -v
    VERY_VERBOSE = 128  # -vv
    DEBUG = 256  # -vvv

V = Verbosity.VERBOSE
VV = Verbosity.VERY_VERBOSE
VVV = Verbosity.DEBUG

class OutputType(IntEnum):
    NORMAL = 1
    RAW = 2


class Output(ABC):
    def __init__(self, verbosity: Verbosity = Verbosity.NORMAL, formatter: Formatter | None = None) -> None:
        from baloto.cleo.formatters.formatter import Formatter

        self.verbosity: Verbosity = verbosity
        self._dev_mode = is_pydevd_mode()
        self._formatter = formatter or Formatter()
        self._section_outputs: list[SectionOutput] = []


    @property
    @abstractmethod
    def console(self) -> Console:
        raise NotImplementedError("[c1]console[/] is an abstract method")

    @property
    @abstractmethod
    def supports_utf8(self) -> bool:
        """
        Returns whether the stream supports the UTF-8 encoding.
        """
        raise NotImplementedError("[c1]supports_utf8[/] is an abstract method")

    @property
    def formatter(self) -> Formatter:
        return self._formatter

    @formatter.setter
    def formatter(self, formatter: Formatter) -> None:
        self._formatter = formatter
        ConsoleFactory.formatter = formatter

    def is_quiet(self) -> bool:
        return self.verbosity is Verbosity.QUIET

    def is_verbose(self) -> bool:
        return self.verbosity.value >= Verbosity.VERBOSE.value

    def is_very_verbose(self) -> bool:
        return self.verbosity.value >= Verbosity.VERY_VERBOSE.value

    def is_debug(self) -> bool:
        return self.verbosity is Verbosity.DEBUG

    def log(
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
        verbosity: Verbosity = Verbosity.NORMAL,
        stack_offset: int = 3,
    ) -> None:

        # if not self._dev_mode:
        #     return
        # if verbosity.value > self.verbosity.value and self._dev_mode:
        #     return
        self._log(
            *objects,
                sep=sep,
                end=end,
                style=style,
                justify=justify,
                markup=markup,
                highlight=highlight,
                log_locals=log_locals,
                emoji=emoji,
                stack_offset=stack_offset
        )

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
        if verbosity.value > self.verbosity.value:
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
    def section(self) -> SectionOutput:
        raise NotImplementedError("[c1]section[/] is an abstract method")

    # @staticmethod
    # def strip_ansi(value: str) -> str:
    #     from click._compat import strip_ansi
    #
    #     return strip_ansi(value)
    #
    # @staticmethod
    # def remove_format(text: str) -> str:
    #     # TODO: test against formatter remove style
    #     text = re.sub(r"\033\[[^m]*m", "", text)
    #     return text

    @abstractmethod
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
        raise NotImplementedError("[c1]_log[/] is an abstract method")

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
    def clear(self, home: bool = True) -> None:
        raise NotImplementedError("[c1]clear[/] is an abstract method")

    @abstractmethod
    def line(self, count: int = 1) -> None:
        raise NotImplementedError("[c1]line[/] is an abstract method")
