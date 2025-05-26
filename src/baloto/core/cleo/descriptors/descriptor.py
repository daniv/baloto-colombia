from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from typing import TYPE_CHECKING

from baloto.core.cleo.application import Application
from baloto.core.cleo.commands.command import Command
from baloto.core.cleo.io.inputs.argument import Argument
from baloto.core.cleo.io.inputs.definition import Definition
from baloto.core.cleo.io.inputs.option import Option
from baloto.core.cleo.io.null_io import NullIO

if TYPE_CHECKING:
    from baloto.core.cleo.io.io import IO
    from rich.console import RenderableType


class Descriptor(ABC):
    def __init__(self) -> None:
        self._io: IO = NullIO()

    def describe(self, io: IO, obj: Any, **options: Any) -> None:
        self._io = io

        if isinstance(obj, Argument):
            self._describe_argument(obj, **options)
        elif isinstance(obj, Option):
            self._describe_option(obj, **options)
        elif isinstance(obj, Definition):
            self._describe_definition(obj, **options)
        elif isinstance(obj, Command):
            self._describe_command(obj, **options)
        elif isinstance(obj, Application):
            self._describe_application(obj, **options)

    @abstractmethod
    def _describe_argument(self, argument: Argument, **options: Any) -> list[RenderableType]:
        raise NotImplementedError("[c1]_describe_argument[/] is an abstract method")

    @abstractmethod
    def _describe_option(self, option: Option, **options: Any) -> list[RenderableType]:
        raise NotImplementedError("[c1]_describe_option[/] is an abstract method")

    @abstractmethod
    def _describe_definition(self, definition: Definition, **options: Any) -> None:
        raise NotImplementedError("[c1]_describe_definition[/] is an abstract method")

    @abstractmethod
    def _describe_command(self, command: Command, **options: Any) -> None:
        raise NotImplementedError("[c1]_describe_command[/] is an abstract method")

    @abstractmethod
    def _describe_application(self, application: Application, **options: Any) -> None:
        raise NotImplementedError("[c1]_describe_application[/] is an abstract method")
