from __future__ import annotations

from typing import TYPE_CHECKING

from baloto.cleo.io.inputs.string_input import StringInput
from baloto.cleo.io.io import IO
from baloto.cleo.io.output import Output

if TYPE_CHECKING:
    from baloto.cleo.io.inputs.input import Input


class BufferedIO(IO):
    def __init__(self, input: Input | None = None) -> None:
        super().__init__(
            input or StringInput(""),
            Output.buffered_output(),
            Output.buffered_output(),
        )

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
        self.input.stream.truncate(0)
        self.input.stream.seek(0)

    def set_user_input(self, user_input: str) -> None:
        self.clear_user_input()

        self.input.stream.write(user_input)
        self.input.stream.seek(0)
