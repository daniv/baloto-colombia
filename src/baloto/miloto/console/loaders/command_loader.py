from __future__ import annotations

from typing import TYPE_CHECKING

from baloto.cleo.exceptions.errors import CleoLogicError
from baloto.cleo.loaders.factory_command_loader import FactoryCommandLoader

if TYPE_CHECKING:
    from collections.abc import Callable
    from baloto.cleo.commands.cleo_command import Command

class CommandLoader(FactoryCommandLoader):
    def register_factory(self, command_name: str, factory: Callable[[], Command]) -> None:
        if command_name in self._factories:
            raise CleoLogicError(f'The command "{command_name}" already exists.')

        self._factories[command_name] = factory
