from __future__ import annotations

import math

from typing import TYPE_CHECKING
from typing import TextIO

from baloto.core.cleo.io.outputs.output import Verbosity
from baloto.core.cleo.io.outputs.stream_output import StreamOutput

# from core.cleo.terminal import Terminal


if TYPE_CHECKING:
    # from core.cleo.formatters.formatter import Formatter
    ...


class SectionOutput(StreamOutput):
    def __init__(
        self,
        stream: TextIO,
        sections: list[SectionOutput],
        verbosity: Verbosity = Verbosity.NORMAL,
        decorated: bool | None = None,
        # formatter: Formatter | None = None,
    ) -> None: ...
