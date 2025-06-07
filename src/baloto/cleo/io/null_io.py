from __future__ import annotations

from typing import TYPE_CHECKING

from baloto.cleo.io.inputs.string_input import StringInput
from baloto.cleo.io.io import IO
from baloto.cleo.io.output import Output
from baloto.cleo.io.outputs.null_output import NullOutput


if TYPE_CHECKING:
    from baloto.cleo.io.inputs.input import Input


class NullIO(IO):
    def __init__(self, input: Input | None = None) -> None:
        null = Output.null_output()
        super().__init__(input or StringInput(""), Output.null_output(), Output.null_output())
