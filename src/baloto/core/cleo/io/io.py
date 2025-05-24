from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import cast

from baloto.core.cleo.io.outputs.output import Type as OutputType
from baloto.core.cleo.io.outputs.output import Verbosity


if TYPE_CHECKING:
    from collections.abc import Iterable

    from baloto.core.cleo.io.inputs.input import Input
    from baloto.core.cleo.io.outputs.output import Output
    from baloto.core.cleo.io.outputs.section_output import SectionOutput
    from rich.console import Console
    from rich.style import Style
    from rich.console import JustifyMethod
    from rich.console import OverflowMethod


class IO:
    def __init__(self, input: Input, output: Output, error_output: Output) -> None:
        self._input = input
        self._output = output
        self._error_output = error_output

    # @property
    # def console(self) -> Console:
    #     from baloto.core.cleo.io.outputs.console_output import ConsoleOutput
    #     if hasattr(self._output, "console"):
    #         output = cast(ConsoleOutput, self._output)
    #         return output.console
    #
    #     raise AttributeError("to get a console the out type shpuld be ConsoleOutput")

    # @property
    # def error_console(self) -> Console | None:
    #     from baloto.core.cleo.io.outputs.console_output import ConsoleOutput
    #     if hasattr(self._error_output, "console"):
    #         output = cast(ConsoleOutput, self._error_output)
    #         return output.console
    #
    #     raise AttributeError("to get a console the out type shpuld be ConsoleOutput")

    @property
    def input(self) -> Input:
        return self._input

    @input.setter
    def input(self, input: Input) -> None:
        self._input = input

    @property
    def output(self) -> Output:
        return self._output

    @output.setter
    def output(self, output: Output) -> None:
        self._output = output

    @property
    def error_output(self) -> Output:
        return self._error_output

    @error_output.setter
    def error_output(self, error_output: Output) -> None:
        self._error_output = error_output

    @property
    def interactive(self) -> bool:
        return self._input.interactive

    @interactive.setter
    def interactive(self, interactive: bool = True) -> None:
        self._input.interactive = interactive

    # @property
    # def supports_utf8(self) -> bool:
    #     return self._output.supports_utf8

    def read(self, length: int, default: str = "") -> str:
        """
        Reads the given amount of characters from the input stream.
        """
        ...

    def read_line(self, length: int = -1, default: str = "") -> str:
        """
        Reads a line from the input stream.
        """
        ...

    def write_error(
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
        self._error_output.write(
            *objects,
            sep=sep,
            end=end,
            justify=justify,
            overflow=overflow,
            style=style,
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
        self._output.write(
            *objects,
            sep=sep,
            end=end,
            justify=justify,
            overflow=overflow,
            style=style,
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

    def overwrite(self, messages: str | Iterable[str]) -> None: ...

    def overwrite_error(self, messages: str | Iterable[str]) -> None: ...

    def flush(self) -> None:
        self._output.flush()

    def set_verbosity(self, verbosity: Verbosity) -> None:
        self._output.set_verbosity(verbosity)
        self._error_output.set_verbosity(verbosity)

    def is_verbose(self) -> bool:
        return self.output.is_verbose()

    def is_very_verbose(self) -> bool:
        return self.output.is_very_verbose()

    def is_debug(self) -> bool:
        return self.output.is_debug()

    def with_input(self, input: Input) -> IO:
        return self.__class__(input, self._output, self._error_output)

    def remove_format(self, text: str) -> str:
        return self._output.remove_format(text)

    def section(self) -> SectionOutput:
        return self._output.section()
