from __future__ import annotations

from abc import ABC
from typing import Self
from typing import TYPE_CHECKING
from typing import TextIO

if TYPE_CHECKING:
    pass


class Input(ABC):
    """
    This class is the base class for concrete Input implementations.
    """

    def __init__(self) -> None:
        self._stream: TextIO = None  # type: ignore[assignment]
        self._interactive: bool | None = None

    def is_interactive(self) -> bool:
        return True if self._interactive is None else self._interactive

    def set_interactive(self, interactive: bool = True) -> None:
        self._interactive = interactive
