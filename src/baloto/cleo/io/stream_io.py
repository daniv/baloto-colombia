# Project : baloto-colombia
# File Name : stream_io.py
# Dir Path : src/baloto/cleo/io
# Created on: 2025–06–08 at 01:52:55.

from __future__ import annotations

import sys
from typing import TYPE_CHECKING
from typing import cast

from baloto.cleo.io.inputs.stream_input import StreamInput
from baloto.cleo.io.io import IO
from baloto.cleo.io.outputs.stream_output import StreamOutput

if TYPE_CHECKING:
    pass

__all__ = ("StreamIO", )

class StreamIO(IO):
    def __init__(self) -> None:

        super().__init__(
            StreamInput(sys.stdin),
            StreamOutput(),
            StreamOutput(stderr=True),
        )

    @property
    def input(self) -> StreamInput:
        return cast(StreamInput, self._input)

    @property
    def output(self) -> StreamOutput:
        return cast(StreamOutput, self._output)

    @property
    def error_output(self) -> StreamOutput:
        return cast(StreamOutput, self._error_output)
