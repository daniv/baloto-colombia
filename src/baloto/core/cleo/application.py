from __future__ import annotations

import os
import re
import sys

from typing import TYPE_CHECKING
from typing import final
from typing import cast
from typing import Iterable

from rich import Console

from baloto.core.cleo.commands.completions_command import CompletionsCommand
from baloto.core.cleo.commands.help_command import HelpCommand
from baloto.core.cleo.commands.list_command import ListCommand
from baloto.core.cleo.events.console_command_event import ConsoleCommandEvent
from baloto.core.cleo.events.console_error_event import ConsoleErrorEvent
from baloto.core.cleo.events.console_events import COMMAND
from baloto.core.cleo.events.console_events import ERROR
from baloto.core.cleo.events.console_events import TERMINATE
from baloto.core.cleo.events.console_terminate_event import ConsoleTerminateEvent
from baloto.core.cleo.exceptions import CleoCommandNotFoundError
from baloto.core.cleo.exceptions import CleoError
from baloto.core.cleo.exceptions import CleoLogicError
from baloto.core.cleo.exceptions import CleoNamespaceNotFoundError
from baloto.core.cleo.exceptions import CleoUserError
from baloto.core.cleo.io.inputs.argument import Argument
from baloto.core.cleo.io.inputs.argv_input import ArgvInput
from baloto.core.cleo.io.inputs.definition import Definition
from baloto.core.cleo.io.inputs.option import Option
from baloto.core.cleo.io.io import IO
from baloto.core.cleo.io.outputs.null_output import NullOutput
from baloto.core.cleo.io.outputs.output import Verbosity
from baloto.core.cleo.io.outputs.console_output import ConsoleOutput


# from core.cleo.terminal import Terminal
# from core.cleo.ui.ui import UI


if TYPE_CHECKING:
    from baloto.core.cleo.commands.command import Command
    from baloto.core.cleo.events.event_dispatcher import EventDispatcher
    from baloto.core.cleo.io.inputs.input import Input
    from baloto.core.cleo.io.outputs.output import Output
    from baloto.core.cleo.loaders.command_loader import CommandLoader
    from rich.console import ModuleType

class Application:
    """
    An Application is the container for a collection of commands.

    This class is optimized for a standard CLI environment.

    Usage:
    >>> app = Application('myapp', '1.0 (stable)')
    >>> app.add(Command())
    >>> app.run()
    """

    def __init__(self, name: str = "console", version: str = "") -> None:
        self._name = name
        self._version = version
        self._display_name: str | None = None
        self._description: str = ""
        self._default_command = "list"
        self._single_command = False
        self._commands: dict[str, Command] = {}
        self._running_command: Command | None = None
        self._want_helps = False
        self._definition: Definition | None = None
        self._catch_exceptions = True
        self._auto_exit = True
        self._initialized = False
        self._event_dispatcher: EventDispatcher | None = None
        self._command_loader: CommandLoader | None = None

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @property
    def display_name(self) -> str:
        if self._display_name is None:
            return re.sub(r"[\s\-_]+", " ", self._name).title()

        return self._display_name

    @display_name.setter
    def display_name(self, display_name: str) -> None:
        self._display_name = display_name

    @property
    def description(self) -> str:
        return self._description

    @property
    def version(self) -> str:
        return self._version

    @version.setter
    def version(self, version: str) -> None:
        self._version = version

    @property
    def long_version(self) -> str:
        if self._name:
            if self._version:
                return f"<b>{self.display_name}</b> (version <c1>{self._version}</c1>)"

            return f"<b>{self.display_name}</b>"

        return "<b>Console</b> application"

    @property
    def definition(self) -> Definition:
        if self._definition is None:
            self._definition = self._default_definition

        if self._single_command:
            definition = self._definition
            definition.set_arguments([])

            return definition

        return self._definition

    @property
    def default_commands(self) -> list[Command]:
        return [HelpCommand(), ListCommand(), CompletionsCommand()]

    @property
    def help(self) -> str:
        return self.long_version

    @property
    def event_dispatcher(self) -> EventDispatcher | None:
        return self._event_dispatcher

    @event_dispatcher.setter
    def event_dispatcher(self, event_dispatcher: EventDispatcher) -> None:
        self._event_dispatcher = event_dispatcher

    @property
    def auto_exits(self) -> bool:
        return self._auto_exit

    @auto_exits.setter
    def auto_exits(self, auto_exits: bool = True) -> None:
        self._auto_exit = auto_exits

    @property
    def catch_exceptions(self) -> bool:
        return self._catch_exceptions

    @catch_exceptions.setter
    def catch_exceptions(self, catch_exceptions: bool = True) -> None:
        self._catch_exceptions = catch_exceptions

    @property
    def single_command(self) -> bool:
        return self._single_command

    @property
    def _default_definition(self) -> Definition:
        return Definition(
            [
                Argument(
                    "command",
                    required=True,
                    description="The command to execute.",
                ),
                Option(
                    "--help",
                    "-h",
                    flag=True,
                    description=(
                        "Display help for the given command. "
                        "When no command is given display help for "
                        f"the <info>{self._default_command}</info> command."
                    ),
                ),
                Option(
                    "--quiet", "-q", flag=True, description="Do not output any message."
                ),
                Option(
                    "--verbose",
                    "-v|vv|vvv",
                    flag=True,
                    description=(
                        "Increase the verbosity of messages: "
                        "1 for normal output, 2 for more verbose "
                        "output and 3 for debug."
                    ),
                ),
                Option(
                    "--version",
                    "-V",
                    flag=True,
                    description="Display this application version.",
                ),
                Option(
                    "--no-interaction",
                    "-n",
                    flag=True,
                    description="Do not ask any interactive question.",
                ),
            ]
        )

    def set_command_loader(self, command_loader: CommandLoader) -> None:
        self._command_loader = command_loader

    def add(self, command: Command) -> Command | None: ...

    def get(self, name: str) -> Command: ...

    def has(self, name: str) -> bool: ...

    def get_namespaces(self) -> list[str]: ...

    def find_namespace(self, namespace: str) -> str: ...

    def find(self, name: str) -> Command: ...

    def all(self, namespace: str | None = None) -> dict[str, Command]: ...

    def run(
        self,
        input: Input | None = None,
        output: Output | None = None,
        error_output: Output | None = None,
    ) -> int: ...

    def _run(self, io: IO) -> int: ...

    def _run_command(self, command: Command, io: IO) -> int: ...

    def create_io(
        self,
        input: Input | None = None,
        output: Output | None = None,
        error_output: Output | None = None,
    ) -> IO:
        if input is None:
            input = ArgvInput()
            input.strem = sys.stdin

        if output is None:
            output = NullOutput(sys.stdout)

        if error_output is None:
            error_output = NullOutput(sys.stderr)

        return IO(input, output, error_output)

    @staticmethod
    def render_error(
            *,
            io: IO,
            error: Exception,
            width: int | None = 100,
            theme: str | None = None,
            word_wrap: bool = False,
            suppress: Iterable[str | ModuleType] = (),
    ) -> None:
        simple = not io.is_verbose() or isinstance(error, CleoUserError)
        assert isinstance(io.error_output, ConsoleOutput)
        if hasattr(io.error_output, "console"):
            console: Console = io.error_output.console

            if simple:
                console.print_exception(
                    width=width, theme=theme, word_wrap=word_wrap, suppress=suppress
                )
            else:
                console: Console = io.error_output.console
                console.print_exception(
                    width=width,
                    word_wrap=word_wrap,
                    extra_lines=4,
                    show_locals=True,
                    theme=theme,
                    suppress=suppress,
                )

    def _configure_io(self, io: IO) -> None: ...

    def _get_command_name(self, io: IO) -> str | None: ...

    def extract_namespace(self, name: str, limit: int | None = None) -> str: ...

    def _extract_all_namespaces(self, name: str) -> list[str]: ...

    def _init(self) -> None:
        if self._initialized:
            return

        self._initialized = True

        for command in self.default_commands:
            self.add(command)
