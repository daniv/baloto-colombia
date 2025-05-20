from __future__ import annotations

from typing import TYPE_CHECKING
from typing import cast

from baloto.core.cleo.io.inputs.string_input import StringInput
from baloto.core.cleo.io.io import IO
from baloto.core.cleo.io.outputs.buffered_output import BufferedOutput


if TYPE_CHECKING:
    from baloto.core.cleo.io.inputs.input import Input


class BufferedIO(IO):
    def __init__(
        self,
        input: Input | None = None,
        decorated: bool = False,
        supports_utf8: bool = True,
    ) -> None:
        super().__init__(
            input or StringInput(""),
            BufferedOutput(decorated=decorated, supports_utf8=supports_utf8),
            BufferedOutput(decorated=decorated, supports_utf8=supports_utf8),
        )
