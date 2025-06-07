from __future__ import annotations

from functools import partialmethod
from typing import TYPE_CHECKING, Any, Iterable

if TYPE_CHECKING:
    from baloto.cleo.io.inputs.input import Input
    from baloto.cleo.io.output import Output, Verbosity, OutputType
    from baloto.cleo.io.outputs.section_output import SectionOutput
    from rich.console import JustifyMethod, OverflowMethod
    from rich.style import Style


class IO:
    def __init__(self, input: Input, output: Output, error_output: Output) -> None:
        self._input = input
        self._output = output
        self._error_output = error_output

    @property
    def input(self) -> Input:
        return self._input

    @input.setter
    def input(self, input: Input) -> None:
        self._input = input

    @property
    def output(self) -> Output:
        return self._output

    @property
    def error_output(self) -> Output:
        return self._error_output

    @property
    def interactive(self) -> bool:
        return self._input.interactive

    @interactive.setter
    def interactive(self, interactive: bool = True) -> None:
        self._input.interactive = interactive

    def read(self, length: int, default: str = "") -> str:
        """
        Reads the given amount of characters from the input stream.
        """
        return self._input.read(length, default=default)

    def read_line(self, length: int = -1, default: str = "") -> str:
        """
        Reads a line from the input stream.
        """
        return self._input.read_line(length=length, default=default)

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
        self.output.write(
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
            verbosity=verbosity,
            type=type,
        )

    def write_error(
        self,
        *objects: Any,
        sep: str = " ",
        end: str = "\n",
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
        self.error_output.write(
            *objects,
            sep=sep,
            end=end,
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
            verbosity=Verbosity.NORMAL,
            type=type,
        )

    def overwrite(self, messages: str | Iterable[str]) -> None:
        from cleo.cursor import Cursor

        cursor = Cursor(self._output)
        cursor.move_to_column(1)
        cursor.clear_line()
        self.write(messages)

    def overwrite_error(self, messages: str | Iterable[str]) -> None:
        from cleo.cursor import Cursor

        cursor = Cursor(self._error_output)
        cursor.move_to_column(1)
        cursor.clear_line()
        self.write_error(messages)

    def flush(self) -> None:
        self._output.flush()

    @property
    def supports_utf8(self) -> bool:
        return self.output.supports_utf8

    def set_verbosity(self, verbosity: Verbosity) -> None:
        self.output.verbosity = verbosity
        self.error_output.verbosity = verbosity

    set_quiet = partialmethod(set_verbosity, Verbosity.QUIET)
    set_normal = partialmethod(set_verbosity, Verbosity.NORMAL)
    set_verbose = partialmethod(set_verbosity, Verbosity.VERBOSE)
    set_very_verbose = partialmethod(set_verbosity, Verbosity.VERY_VERBOSE)
    set_debug = partialmethod(set_verbosity, Verbosity.DEBUG)

    def is_verbose(self) -> bool:
        return self.output.is_verbose()

    def is_very_verbose(self) -> bool:
        return self.output.is_very_verbose()

    def is_debug(self) -> bool:
        return self.output.is_debug()

    def with_input(self, input: Input) -> IO:
        return self.__class__(input, self.output, self.error_output)

    def section(self) -> SectionOutput:
        return self.output.section()
