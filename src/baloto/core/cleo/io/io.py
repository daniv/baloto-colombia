from __future__ import annotations

from typing import TYPE_CHECKING

from baloto.core.cleo.io.outputs.output import Verbosity

if TYPE_CHECKING:
    from baloto.core.cleo.io.inputs.input import Input
    from baloto.core.cleo.io.outputs.output import Output
    from baloto.core.cleo.io.outputs.section_output import SectionOutput


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

    def clear(self) -> None:
        self.output.clear()
