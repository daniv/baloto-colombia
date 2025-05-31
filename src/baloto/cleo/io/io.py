from __future__ import annotations

from typing import TYPE_CHECKING, Any

from baloto.cleo.io.outputs.output import Verbosity, OutputType

if TYPE_CHECKING:
    from baloto.cleo.io.inputs.input import Input
    from baloto.cleo.io.outputs.output import Output
    from baloto.cleo.io.outputs.section_output import SectionOutput
    from rich.console import JustifyMethod, OverflowMethod
    from rich.style import Style


class IO:
    def __init__(self, input: Input, output: Output, error_output: Output) -> None:
        self.input = input
        self.output = output
        self.error_output = error_output

    @property
    def supports_utf8(self) -> bool:
        return self.output.supports_utf8

    def set_verbosity(self, verbosity: Verbosity) -> None:
        self.output.verbosity = verbosity
        self.error_output.verbosity = verbosity

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

    def clear(self, home: bool = True) -> None:
        self.output.clear(home)

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
    ) -> None: ...

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
    ) -> None: ...

    def overwrite(
        self,
        *messages: Any,
    ) -> None:
        from cleo.cursor import Cursor

        cursor = Cursor(self._output)
        cursor.move_to_column(1)
        cursor.clear_line()
        self.write(messages)

    def overwrite_error(self, *messages: Any) -> None:
        from cleo.cursor import Cursor

        cursor = Cursor(self._error_output)
        cursor.move_to_column(1)
        cursor.clear_line()
        self.write_error(messages)

