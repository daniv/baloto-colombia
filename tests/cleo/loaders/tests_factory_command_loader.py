from __future__ import annotations

from functools import partial

from baloto.cleo.commands.command import Command
from baloto.cleo.loaders.factory_command_loader import FactoryCommandLoader
from baloto.core.cleo.exceptions import CleoCommandNotFoundError

"""
A simple command loader using factories to instantiate commands lazily.
"""

import pytest


class TestCommand(Command):
    def __init__(self) -> None:
        super().__init__()

    def handle(self) -> int:
        return 1


@pytest.fixture(scope="module", name="factory_command_loader")
def factory_command_loader() -> FactoryCommandLoader:
    """
    "Creating a FactoryCommandLoader instance"
    """
    def command(name: str) -> Command:
        command_ = TestCommand()
        command_.name = name
        return command_

    return FactoryCommandLoader({"foo": lambda: command("foo"), "bar": lambda: command("bar")})


def method_has_test(factory_command_loader: FactoryCommandLoader) -> None:
    """
    The method returns a boolean value when it contains a command factory by name
    """
    assert factory_command_loader.has("foo"), "The has('foo') method result is unexpected"
    assert factory_command_loader.has("bar"), "The has('bar') method result is unexpected"
    assert not factory_command_loader.has("baz"), "The has('baz') method result is unexpected"


def method_get_test(factory_command_loader: FactoryCommandLoader) -> None:
    """
    "The method returns a Command instance"
    """
    assert isinstance(
        factory_command_loader.get("foo"), Command
    ), "The factory_command_loader instance result is unexpected"
    assert isinstance(
        factory_command_loader.get("bar"), Command
    ), "The factory_command_loader instance result is unexpected"


def method_get_invalid_name_raises_error_test(factory_command_loader: FactoryCommandLoader) -> None:
    """
    The method raises CleoCommandNotFoundError on ivalid command name
    """
    with pytest.raises(CleoCommandNotFoundError) as exc_ifo:
        factory_command_loader.get("baz")

    assert (
        exc_ifo.value.args[0] == 'The command "baz" does not exist.'
    ), "The get('baz') property result is unexpected"


def property_names_test(factory_command_loader: FactoryCommandLoader) -> None:
    """
    The property return a list[str] of commands
    """
    assert factory_command_loader.names == ["foo", "bar"], "The names property result is unexpected"
