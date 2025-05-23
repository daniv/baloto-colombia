from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from typing import TYPE_CHECKING

from baloto.core.cleo.application import Application
from baloto.core.cleo.commands.command import Command
from baloto.core.cleo.io.inputs.argument import Argument
from baloto.core.cleo.io.inputs.definition import Definition
from baloto.core.cleo.io.inputs.option import Option

if TYPE_CHECKING:
    from baloto.core.cleo.io.io import IO
    from rich.console import RenderableType
    from rich.console import Console


class Descriptor(ABC):
    def __init__(self):
        self._io: IO | None = None

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

    @property
    def _console(self) -> Console:
        if hasattr(self._io.output, "console"):
            return self._io.output.console

    @abstractmethod
    def _describe_argument(self, argument: Argument, **options: Any) -> list[RenderableType]: ...

    @abstractmethod
    def _describe_option(self, option: Option, **options: Any) -> list[RenderableType]: ...

    @abstractmethod
    def _describe_definition(self, definition: Definition, **options: Any) -> None: ...

    @abstractmethod
    def _describe_command(self, command: Command, **options: Any) -> None: ...

    @abstractmethod
    def _describe_application(self, application: Application, **options: Any) -> None: ...
