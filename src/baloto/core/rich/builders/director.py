from __future__ import annotations

from typing import cast

from baloto.core.patterns.builder import Director
from baloto.core.rich.builders.console_builder import ConsoleBuilder

__all__ = ["RichDirector"]


class RichDirector(Director):

    def __init__(self) -> None:
        super().__init__()
        self.reset()

    def reset(self) -> None:
        self._builder = None

    def console_builder(self, **kwargs) -> ConsoleBuilder: # type: ignore[no-untyped-def]
        self._builder = ConsoleBuilder(**kwargs)
        return self._builder

