from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from baloto.core.cleo.io.outputs.output import Output
from baloto.core.cleo.io.outputs.output import Verbosity
from baloto.core.cleo.io.outputs.section_output import SectionOutput

if TYPE_CHECKING:
    from rich.style import Style
    from rich.console import JustifyMethod
    from rich.console import OverflowMethod


class NullOutput(Output):

    @property
    def verbosity(self) -> Verbosity:
        return Verbosity.QUIET

    @verbosity.setter
    def verbosity(self, verbosity: Verbosity) -> None:
        pass

    # def supports_utf8(self) -> bool:
    #     return True

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

    def _write(
        self,
        *objects: Any,
        sep: str = " ",
        end: str = "\n",
        style: str | Style | None = None,
        justify: JustifyMethod | None = None,
        overflow: OverflowMethod | None = None,
        no_wrap: bool | None = None,
        markup: bool | None = None,
        highlight: bool = True,
        width: int | None = None,
        height: int | None = None,
        crop: bool = True,
        soft_wrap: bool | None = None,
        new_line_start: bool = False,
    ) -> None:
        pass
