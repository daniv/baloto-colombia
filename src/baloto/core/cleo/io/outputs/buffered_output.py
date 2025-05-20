from __future__ import annotations

from io import StringIO
from typing import TYPE_CHECKING

from baloto.core.cleo.io.outputs.output import Output
from baloto.core.cleo.io.outputs.output import Verbosity
from baloto.core.cleo.io.outputs.section_output import SectionOutput


if TYPE_CHECKING:
    from baloto.core.cleo.formatters.formatter import Formatter


class BufferedOutput(Output):
    def __init__(
        self,
        verbosity: Verbosity = Verbosity.NORMAL,
        decorated: bool = False,
        formatter: Formatter | None = None,
        supports_utf8: bool = True,
    ) -> None: ...
