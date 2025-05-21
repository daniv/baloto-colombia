from __future__ import annotations

import contextlib
import os
import re
import shutil
import sys
from abc import abstractmethod

from typing import TYPE_CHECKING
from typing import final
from typing import cast
from typing import Iterable

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
    from rich.console import Console

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
        self._terminal_size = shutil.get_terminal_size()
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
                return f"[b]{self.display_name}[/] (version [repr.number]{self._version}[/])"

            return f"[b]{self.display_name}[/]"

        return "[b]Console[/] application"

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
        # return [HelpCommand(), ListCommand(), CompletionsCommand()]
        return [HelpCommand(), ListCommand()]

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
    @abstractmethod
    def console(self) -> Console: ...

    @property
    @abstractmethod
    def error_console(self) -> Console: ...

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
                        f"the [info]{self._default_command}[/info] command."
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

    @staticmethod
    def is_debug_mode() -> bool:
        get_trace = getattr(sys, "gettrace", None)
        return False if get_trace is None else True

    def set_command_loader(self, command_loader: CommandLoader) -> None:
        self._command_loader = command_loader

    def add(self, command: Command) -> Command | None:
        self._init()

        command.application = self

        if not command.enabled:
            command.application = None

            return None

        if not command.name:
            raise CleoLogicError(
                f'The command "{command.__class__.__name__}" cannot have an empty name'
            )

        self._commands[command.name] = command

        for alias in command.aliases:
            self._commands[alias] = command

        return command

    def get(self, name: str) -> Command:
        self._init()

        if not self.has(name):
            raise CleoCommandNotFoundError(name)

        if name not in self._commands:
            # The command was registered in a different name in the command loader
            raise CleoCommandNotFoundError(name)

        command = self._commands[name]

        if self._want_helps:
            self._want_helps = False

            help_command: HelpCommand = cast("HelpCommand", self.get("help"))
            help_command.set_command(command)

            return help_command

        return command

    def has(self, name: str) -> bool:
        self._init()

        if name in self._commands:
            return True

        if not self._command_loader:
            return False

        return bool(
            self._command_loader.has(name) and self.add(self._command_loader.get(name))
        )

    def get_namespaces(self) -> list[str]: ...

    def find_namespace(self, namespace: str) -> str:
        if namespace not in (all_namespaces := self.get_namespaces()):
            raise CleoNamespaceNotFoundError(namespace, all_namespaces)
        return namespace

    def find(self, name: str) -> Command:
        self._init()

        if self.has(name):
            return self.get(name)

        all_commands = []
        if self._command_loader:
            all_commands += self._command_loader.names

        all_commands += [
            name for name, command in self._commands.items() if not command.hidden
        ]

        raise CleoCommandNotFoundError(name, all_commands)

    def all(self, namespace: str | None = None) -> dict[str, Command]:
        self._init()

        if namespace is None:
            commands = self._commands.copy()
            if not self._command_loader:
                return commands

            for name in self._command_loader.names:
                if name not in commands and self.has(name):
                    commands[name] = self.get(name)

            return commands

        commands = {}

        for name, command in self._commands.items():
            if namespace == self.extract_namespace(name, name.count(" ") + 1):
                commands[name] = command

        if self._command_loader:
            for name in self._command_loader.names:
                if (
                        name not in commands
                        and namespace == self.extract_namespace(name, name.count(" ") + 1)
                        and self.has(name)
                ):
                    commands[name] = self.get(name)

        return commands

    def run(
        self,
        input: Input | None = None,
        output: Output | None = None,
        error_output: Output | None = None,
    ) -> int:

        try:
            io = self.create_io(input, output, error_output)

            self._configure_io(io)

            try:
                exit_code = self._run(io)
            except BrokenPipeError:
                # TODO: io.output.on_broken_pipe()
                # If we are piped to another process, it may close early and send a
                # SIGPIPE: https://docs.python.org/3/library/signal.html#note-on-sigpipe
                devnull = os.open(os.devnull, os.O_WRONLY)
                os.dup2(devnull, sys.stdout.fileno())
                exit_code = 0
            except Exception as e:
                if not self._catch_exceptions:
                    raise

                width = None if self.is_debug_mode() else self._terminal_size.columns
                self.render_error(io=io, error=e, width=width)

                exit_code = 1
                # TODO: Custom error exit codes
        except KeyboardInterrupt:
            exit_code = 1

        if self._auto_exit:
            sys.exit(exit_code)

        return exit_code

    def _run(self, io: IO) -> int:
        if io.input.has_parameter_option(["--version", "-V"], True):
            self.console.print(self.long_version)
            return 0

        definition = self.definition
        input_definition = Definition()
        for argument in definition.arguments:
            if argument.name == "command":
                argument = Argument(
                    "command",
                    required=True,
                    is_list=True,
                    description=definition.argument("command").description,
                )

            input_definition.add_argument(argument)

        input_definition.set_options(definition.options)

        # Errors must be ignored, full binding/validation
        # happens later when the command is known.
        with contextlib.suppress(CleoError):
            # Makes ArgvInput.first_argument() able to
            # distinguish an option from an argument.
            io.input.bind(input_definition)

        name = self._get_command_name(io)
        if io.input.has_parameter_option(["--help", "-h"], True):
            if not name:
                name = "help"
                io.input = ArgvInput(["console", "help", self._default_command])
            else:
                self._want_helps = True

        if not name:
            name = self._default_command
            definition = self.definition
            arguments = definition.arguments
            if not definition.has_argument("command"):
                arguments.append(
                    Argument(
                        "command",
                        required=False,
                        description=definition.argument("command").description,
                        default=name,
                    )
                )
            definition.set_arguments(arguments)

        self._running_command = None
        command = self.find(name)

        self._running_command = command

        if " " in name and isinstance(io.input, ArgvInput):
            # If the command is namespaced we rearrange
            # the input to parse it as a single argument
            argv = io.input._tokens[:]

            if io.input.script_name is not None:
                argv.insert(0, io.input.script_name)

            namespace = name.split(" ")[0]
            index = None
            for i, arg in enumerate(argv):
                if arg == namespace and i > 0:
                    argv[i] = name
                    index = i
                    break

            if index is not None:
                del argv[index + 1: index + 1 + name.count(" ")]

            stream = io.input.stream
            interactive = io.input.interactive
            io.input = ArgvInput(argv)
            io.input.stream = stream
            io.input.interactive = interactive

        exit_code = self._run_command(command, io)
        self._running_command = None

        return exit_code

    def _run_command(self, command: Command, io: IO) -> int:
        if self._event_dispatcher is None:
            return command.run(io)

            # Bind before the console.command event,
            # so the listeners have access to the arguments and options
        try:
            command.merge_application_definition()
            io.input.bind(command.definition)
        except CleoError:
            # Ignore invalid option/arguments for now,
            # to allow the listeners to customize the definition
            pass

        command_event = ConsoleCommandEvent(command, io)
        error = None

        try:
            self._event_dispatcher.dispatch(command_event, COMMAND)

            if command_event.command_should_run():
                exit_code = command.run(io)
            else:
                exit_code = ConsoleCommandEvent.RETURN_CODE_DISABLED
        except Exception as e:
            error_event = ConsoleErrorEvent(command, io, e)
            self._event_dispatcher.dispatch(error_event, ERROR)
            error = error_event.error
            exit_code = error_event.exit_code

            if exit_code == 0:
                error = None

        terminate_event = ConsoleTerminateEvent(command, io, exit_code)
        self._event_dispatcher.dispatch(terminate_event, TERMINATE)

        if error is not None:
            raise error

        return terminate_event.exit_code

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

    def _configure_io(self, io: IO) -> None:
        if io.input.has_parameter_option(["--no-interaction", "-n"], True) or (
                io.input.interactive is None
                and io.input.stream
                and not io.input.stream.isatty()
        ):
            io.interactive = False

        shell_verbosity = int(os.getenv("SHELL_VERBOSITY", 0))
        if io.input.has_parameter_option(["--quiet", "-q"], True):
            io.set_verbosity(Verbosity.QUIET)
            shell_verbosity = -1
        else:
            if io.input.has_parameter_option("-vvv", True):
                io.set_verbosity(Verbosity.DEBUG)
                shell_verbosity = 3
            elif io.input.has_parameter_option("-vv", True):
                io.set_verbosity(Verbosity.VERY_VERBOSE)
                shell_verbosity = 2
            elif io.input.has_parameter_option(
                    "-v", True
            ) or io.input.has_parameter_option("--verbose", only_params=True):
                io.set_verbosity(Verbosity.VERBOSE)
                shell_verbosity = 1

        if shell_verbosity == -1:
            io.interactive = False

    def _get_command_name(self, io: IO) -> str | None:
        if self._single_command:
            return self._default_command

        if "command" in io.input.arguments and io.input.argument("command"):
            candidates: list[str] = []
            for command_part in io.input.argument("command"):
                if candidates:
                    candidates.append(candidates[-1] + " " + command_part)
                else:
                    candidates.append(command_part)

            for candidate in reversed(candidates):
                if self.has(candidate):
                    return candidate

        return io.input.first_argument

    @staticmethod
    def extract_namespace(name: str, limit: int | None = None) -> str:
        parts = name.split(" ")[:-1]
        return " ".join(parts[:limit])

    @staticmethod
    def _extract_all_namespaces(self, name: str) -> list[str]:
        parts = name.split(" ")[:-1]
        namespaces: list[str] = []

        for part in parts:
            namespaces.append(namespaces[-1] + " " + part if namespaces else part)

        return namespaces

    def _init(self) -> None:
        if self._initialized:
            return

        self._initialized = True

        for command in self.default_commands:
            self.add(command)
