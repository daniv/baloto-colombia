from __future__ import annotations

from typing import TYPE_CHECKING
from typing import cast

from baloto.cleo.io.inputs.string_input import StringInput
from baloto.cleo.io.io import IO
from baloto.cleo.io.outputs.buffered_output import BufferedOutput

if TYPE_CHECKING:
    from baloto.cleo.io.inputs.input import Input
    from rich.console import Console


class BufferedIO(IO):
    def __init__(self, console: Console, input: Input | None = None) -> None:
        super().__init__(
            input or StringInput(""),
            BufferedOutput(console),
            BufferedOutput(console),
        )

    def fetch_output(self) -> str:
        return cast("BufferedOutput", self.output).fetch()

    def fetch_error(self) -> str:
        return cast("BufferedOutput", self.error_output).fetch()

    def clear(self, home: bool = True) -> None:
        cast("BufferedOutput", self.output).clear(home)
        cast("BufferedOutput", self.error_output).clear(home)

    def clear_output(self) -> None:
        cast("BufferedOutput", self.output).clear(False)

    def clear_error(self) -> None:
        cast("BufferedOutput", self.error_output).clear(False)

    @property
    def supports_utf8(self) -> bool:
        return cast("BufferedOutput", self.output).supports_utf8

    def clear_user_input(self) -> None:
        self.input.stream.truncate(0)
        self.input.stream.seek(0)

    def set_user_input(self, user_input: str) -> None:
        self.clear_user_input()

        self.input.stream.write(user_input)
        self.input.stream.seek(0)