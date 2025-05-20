from __future__ import annotations

import codecs
import io
import locale
import os
import sys

from typing import TYPE_CHECKING
from typing import TextIO
from typing import cast

from baloto.core.cleo.io.outputs.output import Output
from baloto.core.cleo.io.outputs.output import Verbosity


if TYPE_CHECKING:
    from baloto.core.cleo.formatters.formatter import Formatter
    from baloto.core.cleo.io.outputs.section_output import SectionOutput


class StreamOutput(Output):
    FILE_TYPE_CHAR = 0x0002
    FILE_TYPE_REMOTE = 0x8000
    ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004

    def __init__(
        self,
        stream: TextIO,
        verbosity: Verbosity = Verbosity.NORMAL,
        decorated: bool | None = None,
        formatter: Formatter | None = None,
    ) -> None: ...
