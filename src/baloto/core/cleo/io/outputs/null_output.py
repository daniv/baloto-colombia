from __future__ import annotations

from typing import TYPE_CHECKING

from baloto.core.cleo.io.outputs.output import Output
from baloto.core.cleo.io.outputs.output import Type
from baloto.core.cleo.io.outputs.output import Verbosity


if TYPE_CHECKING:
    from collections.abc import Iterable


class NullOutput(Output): ...
