from __future__ import annotations

from baloto.core.cleo.commands.command import Command
from baloto.core.cleo.exceptions import CleoCommandNotFoundError
from baloto.core.cleo.io.io import IO
from baloto.core.cleo.loaders.factory_command_loader import FactoryCommandLoader

"""
A simple command loader using factories to instantiate commands lazily.
"""

import pytest


def factory_command_loader_step() -> FactoryCommandLoader:
    """
    "Creating a FactoryCommandLoader instance"
    """

    class TestCommand(Command):
        def __init__(self):
            super().__init__()

        def handle(self) -> int:
            pass

    def command(name: str) -> Command:
        command_ = TestCommand()
        command_.name = name
        return command_

    return FactoryCommandLoader({"foo": lambda: command("foo"), "bar": lambda: command("bar")})


def method_has_test():
    """
    The method returns a boolean value when it contains a command factory by name
    """
    factory_command_loader = factory_command_loader_step()
    assert factory_command_loader.has("foo"), "The has('foo') method result is unexpected"
    assert factory_command_loader.has("bar"), "The has('bar') method result is unexpected"
    assert not factory_command_loader.has("baz"), "The has('baz') method result is unexpected"


def method_get_test() -> None:
    """
    "The method returns a Command instance"
    """
    factory_command_loader = factory_command_loader_step()
    assert isinstance(
        factory_command_loader.get("foo"), Command
    ), "The factory_command_loader instance result is unexpected"
    assert isinstance(
        factory_command_loader.get("bar"), Command
    ), "The factory_command_loader instance result is unexpected"


def get_invalid_command_raises_error_test() -> None:
    """
    The method raises CleoCommandNotFoundError on ivalid command name
    """
    factory_command_loader = factory_command_loader_step()

    with pytest.raises(CleoCommandNotFoundError):
        factory_command_loader.get("baz")


def property_names_test() -> None:
    """
    The property return a list[str] of commands
    """
    factory_command_loader = factory_command_loader_step()
    assert factory_command_loader.names == ["foo", "bar"], "The names property result is unexpected"
