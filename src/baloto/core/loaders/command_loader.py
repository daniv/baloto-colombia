from __future__ import annotations

from typing import TYPE_CHECKING
from importlib import import_module

from baloto.core.cleo.exceptions import CleoLogicError
from baloto.core.cleo.loaders.factory_command_loader import FactoryCommandLoader

if TYPE_CHECKING:
    from collections.abc import Callable

    from baloto.core.commands.command import Command


def load_command(package: str, name: str) -> Callable[[], Command]:
    def _load() -> Command:
        words = name.split(" ")
        module = import_module(package + ".".join(words))
        command_class = getattr(module, "".join(c.title() for c in words) + "Command")
        command: Command = command_class()
        return command

    return _load


class CommandLoader(FactoryCommandLoader):
    def register_factory(self, command_name: str, factory: Callable[[], Command]) -> None:
        if command_name in self._factories:
            raise CleoLogicError(f'The command "{command_name}" already exists.')

        self._factories[command_name] = factory
