from __future__ import annotations

from typing import TYPE_CHECKING

from baloto.core.cleo.io.outputs.output import Output
from baloto.core.cleo.io.outputs.output import Type
from baloto.core.cleo.io.outputs.output import Verbosity
from baloto.core.cleo.io.outputs.section_output import SectionOutput

if TYPE_CHECKING:
    from collections.abc import Iterable


class NullOutput(Output):

    @property
    def verbosity(self) -> Verbosity:
        return Verbosity.QUIET

    @verbosity.setter
    def verbosity(self, verbosity: Verbosity) -> None:
        pass

    def supports_utf8(self) -> bool:
        return True

    def is_quiet(self) -> bool:
        return True

    def is_verbose(self) -> bool:
        return False

    def is_very_verbose(self) -> bool:
        return False

    def is_debug(self) -> bool:
        return False

    def section(self) -> SectionOutput:
        pass

    def _write(self, message: str, new_line: bool = False) -> None:
        pass

