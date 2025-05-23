from __future__ import annotations

from io import StringIO
from typing import TYPE_CHECKING
from typing import TextIO
from typing import Any

from baloto.core.cleo.io.outputs.output import Output
from baloto.core.cleo.io.outputs.output import Verbosity


if TYPE_CHECKING:
    from rich.console import Console
    from rich.style import Style
    from rich.console import JustifyMethod
    from rich.console import OverflowMethod


class SectionOutput(Output):
    def __init__(
        self,
        stream: TextIO | Console,
        sections: list[SectionOutput],
        supports_utf8: bool = True,
        verbosity: Verbosity = Verbosity.NORMAL,
    ) -> None:
        super().__init__(verbosity)

        self._supports_utf8 = supports_utf8
        self._buffer = StringIO()

    def set_supports_utf8(self, supports_utf8: bool) -> None:
        self._supports_utf8 = supports_utf8

    @property
    def supports_utf8(self) -> bool:
        return self._supports_utf8

    def fetch(self) -> str:
        """
        Empties the buffer and returns its content.
        """
        content = self._buffer.getvalue()
        self._buffer = StringIO()

        return content

    def clear(self) -> None:
        """
        Empties the buffer.
        """
        self._buffer = StringIO()

    def section(self) -> SectionOutput:
        return SectionOutput(
            self._buffer,
            self._section_outputs,
            verbosity=self.verbosity,
        )

    def _write(
        self,
        *objects: Any,
        sep: str = " ",
        end: str = "",
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
        if len(objects) == 1:
            message = str(objects[0])
            if new_line_start:
                self._buffer.write("\n")
            self._buffer.write(message)
            if end:
                self._buffer.write(end)
        else:
            raise ValueError("SectionOutput supports only one message")
