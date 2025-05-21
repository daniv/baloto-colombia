from __future__ import annotations

import math

from typing import TYPE_CHECKING
from typing import TextIO

from baloto.core.cleo.io.outputs.output import Verbosity
from baloto.core.cleo.io.outputs.console_output import ConsoleOutput

# from core.cleo.terminal import Terminal


if TYPE_CHECKING:
    # from core.cleo.formatters.formatter import Formatter
    from rich.console import Console


class SectionOutput(ConsoleOutput):
    def __init__(
            self,
            stream: TextIO,
            sections: list[SectionOutput],
            console: Console,
            verbosity: Verbosity = Verbosity.NORMAL) -> None:
        super().__init__(console, verbosity)
        ...
