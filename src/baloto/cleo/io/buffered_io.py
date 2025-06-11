from __future__ import annotations

from typing import TYPE_CHECKING
from typing import cast

from baloto.cleo.io.inputs.string_input import StringInput
from baloto.cleo.io.io import IO
from baloto.cleo.io.outputs.buffered_output import BufferedOutput
from baloto.cleo.rich.console_factory import ConsoleFactory

if TYPE_CHECKING:
    from baloto.cleo.io.inputs.input import Input


class BufferedIO(IO):
    def __init__(self, input: Input | None = None) -> None:
        input_ = input or StringInput("")

        super().__init__(input_, BufferedOutput(), BufferedOutput())

    @property
    def input(self) -> StringInput:
        return cast(StringInput, self._input)

    @property
    def output(self) -> BufferedOutput:
        return cast(BufferedOutput, self._output)

    @property
    def error_output(self) -> BufferedOutput:
        return cast(BufferedOutput, self._error_output)

    def fetch_output(self) -> str:
        return self.output.fetch()

    def fetch_error(self) -> str:
        return self.error_output.fetch()

    def clear(self) -> None:
        self.output.clear()
        self.error_output.clear()

    def clear_output(self) -> None:
        self.output.clear()

    def clear_error(self) -> None:
        self.error_output.clear()

    @property
    def supports_utf8(self) -> bool:
        return self.output.supports_utf8

    def clear_user_input(self) -> None:
        self._input.stream.truncate(0)
        self._input.stream.seek(0)

    def set_user_input(self, user_input: str) -> None:
        self.clear_user_input()

        self._input.stream.write(user_input)
        self._input.stream.seek(0)

