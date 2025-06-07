# - Project   : baloto-colombia
# - User Naem : solma
# - File Name : application.py
# - Dir Path  : src/baloto/cleo
# - Created on: 2025-05-30 at 21:05:08

from __future__ import annotations

import contextlib
import logging
import os
import re
import shutil
import sys
from types import ModuleType
from typing import TYPE_CHECKING, cast, Iterable

# from baloto.cleo.decorator import set_verbositye, log, set_rich_console
from baloto.cleo.events.console_command_event import ConsoleCommandEvent
from baloto.cleo.events.console_error_event import ConsoleErrorEvent
from baloto.cleo.events.console_events import COMMAND, TERMINATE, ERROR
from baloto.cleo.events.console_terminate_event import ConsoleTerminateEvent
from baloto.cleo.exceptions.errors import (
    CleoLogicError,
    CleoCommandNotFoundError,
    CleoNamespaceNotFoundError,
    CleoError,
    CleoUserError,
)
from baloto.cleo.io.inputs.argument import Argument
from baloto.cleo.io.inputs.argv_input import ArgvInput
from baloto.cleo.io.inputs.option import Option
from baloto.cleo.io.outputs.output import Verbosity

if TYPE_CHECKING:
    from baloto.cleo.events.event_dispatcher import EventDispatcher
    from rich.console import Console
    from baloto.cleo.commands.cleo_command import Command
    from baloto.cleo.io.inputs.definition import Definition
    from baloto.cleo.io.inputs.input import Input

    from baloto.cleo.io.io import IO


    from baloto.cleo.io.outputs.output import Output
    from baloto.cleo.loaders.command_loader import CommandLoader


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
        self.name = name
        self.description: str = ""
        self.version = version
        self.event_dispatcher: EventDispatcher | None = None
        self.auto_exit = True
        self.catch_exceptions = True
        self.single_command = False
        self._display_name: str | None = None
        self._default_command = "list"
        self._commands: dict[str, Command] = dict()
        self._running_command: Command | None = None
        self._want_helps = False
        self._definition: Definition | None = None
        self._command_loader: CommandLoader | None = None
        self._terminal_size = shutil.get_terminal_size()
        self._initialized = False

        from baloto.utils import is_pydevd_mode
        self.is_pydevd_mode = is_pydevd_mode()

    @property
    def help(self) -> str:
        return self.long_version

    @property
    def display_name(self) -> str:
        if self._display_name is None:
            return re.sub(r"[\s\-_]+", " ", self.name).title()

        return self._display_name

    @display_name.setter
    def display_name(self, display_name: str) -> None:
        self._display_name = display_name

    @property
    def long_version(self) -> str:
        if self.name:
            if self.version:
                return f"[b]{self.display_name}[/] (version [repr.number]{self.version}[/])"

            return f"[b]{self.display_name}[/]"

        return "[b]Console[/] application"

    def set_command_loader(self, command_loader: CommandLoader) -> None:
        self._command_loader = command_loader

    @property
    def definition(self) -> Definition:
        if self._definition is None:
            self._definition = self.default_definition()

        if self.single_command:
            definition = self._definition
            definition.set_arguments([])

            return definition

        return self._definition

    @staticmethod
    def create_io(
        input: Input | None = None,
        output: Output | None = None,
        error_output: Output | None = None,
    ) -> IO:

        from baloto.cleo.io.outputs.null_output import NullOutput
        from baloto.cleo.io.io import IO

        if input is None:
            input = ArgvInput()
            input.stream = sys.stdin

        if output is None:
            output = NullOutput()

        if error_output is None:
            error_output = NullOutput()

        return IO(input, output, error_output)

    # @log
    def run(
        self,
        input: Input | None = None,
        output: Output | None = None,
        error_output: Output | None = None,
    ) -> int:
        try:
            io = self.create_io(input, output, error_output)
            # set_rich_console(io.output.console)

            # from baloto.cleo.decorator import get_rich_console

            self._configure_io(io)
            self._configure_logging(io)

            try:
                exit_code = self._run(io)
            except BrokenPipeError:
                # TODO: io.output.on_broken_pipe()
                # If we are piped to another process, it may close early and send a
                # SIGPIPE: https://docs.python.org/3/library/signal.html#note-on-sigpipe
                devnull = os.open(os.devnull, os.O_WRONLY)
                os.dup2(devnull, sys.stdout.fileno())
                exit_code = 0
                if io:
                    io.error_output.console.on_broken_pipe()
                    io.output.console.on_broken_pipe()

            except Exception as error:
                if not self.catch_exceptions:
                    raise

                self.render_trace(error, io)

                width = None if self.is_pydevd_mode else self._terminal_size.columns
                self.render_error(io=io, error=error, width=width)

                exit_code = 1
                # TODO: Custom error exit codes
        except KeyboardInterrupt:
            exit_code = 1

        if self.auto_exit:
            sys.exit(exit_code)

        return exit_code

    @staticmethod
    def render_trace(error: Exception, io: IO) -> None:
        i = 0
        # from baloto.cleo.exceptions.exception_trace.component import ExceptionTrace
        #
        # trace = ExceptionTrace(error)
        # simple = not io.is_verbose() or isinstance(error, CleoUserError)
        # trace.render(io.error_output, simple)

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
        from baloto.cleo.io.outputs.console_output import ConsoleOutput

        simple = not io.is_verbose() or isinstance(error, CleoUserError)
        assert isinstance(io.error_output, ConsoleOutput)
        console: Console = io.error_output.console
        if hasattr(io.error_output, "console"):

            if simple:
                console.print_exception(width=width, theme=theme, word_wrap=word_wrap, suppress=suppress)
            else:
                from rich.traceback import Traceback

                traceback = Traceback(
                    width=width,
                    extra_lines=4,
                    theme=theme,
                    word_wrap=word_wrap,
                    show_locals=True,
                    suppress=suppress,
                    # max_frames=max_frames,
                )
                console.print(traceback)

                # console.print_exception(
                #     width=width,
                #     word_wrap=word_wrap,
                #     extra_lines=4,
                #     show_locals=True,
                #     theme=theme,
                #     suppress=suppress,
                # )

    @staticmethod
    def default_commands() -> list[Command]:
        # return [HelpCommand(), ListCommand(), CompletionsCommand()]
        from baloto.cleo.commands.help_command import HelpCommand
        from baloto.cleo.commands.list_command import ListCommand

        return [HelpCommand(), ListCommand()]

    def default_definition(self) -> Definition:
        from baloto.cleo.io.inputs.definition import Definition
        return Definition(
            definition=[
                Argument.make(
                    "command",
                    required=True,
                    description="The command to execute.",
                ),
                Option.make(
                    "--help",
                    "-h",
                    flag=True,
                    description=(
                        "Display help for the given command. "
                        "When no command is given display help for "
                        f"the [info]{self._default_command}[/info] command."
                    ),
                ),
                Option.make("--quiet", "-q", flag=True, description="Do not output any message."),
                Option.make(
                    "--verbose",
                    "-v|vv|vvv",
                    flag=True,
                    description=(
                        "Increase the verbosity of messages: "
                        "1 for normal output, 2 for more verbose "
                        "output and 3 for debug."
                    ),
                ),
                Option.make(
                    "--version",
                    "-V",
                    flag=True,
                    description="Display this application version.",
                ),
                Option.make("--no-ansi", flag=True, description="Disable [b]ANSI[/] output."),
                Option.make("--ansi", flag=True, description="Force [b]ANSI[/] output."),
            ]
        )

    def add(self, command: Command) -> Command | None:
        self._init()

        command.application = self

        if not command.enabled:
            command.application = None

            return None

        # TODO: already validated?
        if not command.name:
            raise CleoLogicError(
                f'The command "{command.__class__.__name__}" cannot have an empty name', "cmd-empty-name"
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

            from baloto.cleo.commands.help_command import HelpCommand
            help_command = cast(HelpCommand, self.get("help"))
            help_command.set_command(command)

            return help_command

        return command

    def has(self, name: str) -> bool:
        self._init()

        if name in self._commands:
            return True

        if not self._command_loader:
            return False

        return bool(self._command_loader.has(name) and self.add(self._command_loader.get(name)))

    def get_namespaces(self) -> list[str]:
        namespaces = []
        seen = set()

        for command in self.all().values():
            if command.hidden or not command.name:
                continue

            for namespace in self._extract_all_namespaces(command.name):
                if namespace in seen:
                    continue

                namespaces.append(namespace)
                seen.add(namespace)

            for alias in command.aliases:
                for namespace in self._extract_all_namespaces(alias):
                    if namespace in seen:
                        continue

                    namespaces.append(namespace)
                    seen.add(namespace)

        return namespaces

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

        all_commands += [name for name, command in self._commands.items() if not command.hidden]

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

    @staticmethod
    def extract_namespace(name: str, limit: int | None = None) -> str:
        parts = name.split(" ")[:-1]
        return " ".join(parts[:limit])

    @staticmethod
    def _extract_all_namespaces(name: str) -> list[str]:
        parts = name.split(" ")[:-1]
        namespaces: list[str] = []

        for part in parts:
            namespaces.append(namespaces[-1] + " " + part if namespaces else part)

        return namespaces

    def _get_command_name(self, io: IO) -> str | None:
        if self.single_command:
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

    # @log
    def _configure_logging(self, io: IO) -> None:
        """
        Configures the built-in logging package to write it's output via Cleo's output class.
        """

        # TODO: check if alreay set to avoid duplication

        logging_level = level_mapping[io.output.verbosity]
        level_name = logging.getLevelName(logging_level)
        root = logging.getLogger()
        root.setLevel(logging_level)

        from baloto.cleo.rich.logging.console_handler import ConsoleHandler

        rich_tracebacks = True if logging_level <= logging.INFO else False
        tracebacks_show_locals = logging_level == logging.DEBUG

        if self.is_pydevd_mode:
            rich_tracebacks = True
            tracebacks_show_locals = True

        handler = ConsoleHandler(
                level=logging_level,
                console=io.output.console,
                rich_tracebacks=rich_tracebacks,
                tracebacks_show_locals=tracebacks_show_locals,
                keywords=["APP"]
        )

        handler.setLevel(level_mapping[io.output.verbosity])
        root.addHandler(handler)
        logging.debug(f"[APP] logging was set successfuly, current level is {level_name}")
        io.output.log(
            f"[APP] logging was set successfuly, current level is [{level_name.lower()}]{level_name}[/]")

    @staticmethod
    def _configure_io(io: IO) -> None:

        # io.output.log("Configuring IO on Cleo application")
        # io.output.log("Determine level of verbosity")

        shell_verbosity = int(os.getenv("SHELL_VERBOSITY", 0))
        if io.input.has_parameter_option(["--quiet", "-q"], True):
            io.set_quiet()
            # io.output.log("Verbosity level will be Verbosity.QUIET")
            shell_verbosity = -1
        else:
            if io.input.has_parameter_option("-vvv", True):
                io.set_debug()
                # io.output.log("Verbosity level will be Verbosity.DEBUG")
                shell_verbosity = 3
            elif io.input.has_parameter_option("-vv", True):
                io.set_very_verbose()
                # io.output.log("Verbosity level will be Verbosity.VERY_VERBOSE")
                shell_verbosity = 2
            elif io.input.has_parameter_option("-v", True) or io.input.has_parameter_option(
                "--verbose", only_params=True
            ):
                io.set_verbose()
                # io.output.log("Verbosity level will be Verbosity.VERBOSE")
                shell_verbosity = 1

        if shell_verbosity == -1:
            io.input.interactive = False

        # io.output.log("setting verbosity level for function decorator [yellow]@log[/]")
        # set_verbositye(io.output.verbosity)

    def _init(self) -> None:
        if self._initialized:
            return

        self._initialized = True

        for command in self.default_commands():
            self.add(command)

    # @log
    def _run(self, io: IO) -> int:
        from baloto.cleo.io.inputs.definition import Definition

        if io.input.has_parameter_option(["--version", "-V"], True):
            io.output.write(self.long_version)
            return 0

        definition = self.definition
        input_definition = Definition()
        for argument in definition.arguments():
            if argument.name == "command":
                argument = Argument.make(
                    "command",
                    required=True,
                    is_list=True,
                    description=definition.argument("command").description,
                )

            input_definition.add_argument(argument)

        input_definition.set_options(list(definition.options()))

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
                    Argument.make(
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
                del argv[index + 1 : index + 1 + name.count(" ")]

            # stream = io.input.stream
            # interactive = io.input.interactive
            io.input = ArgvInput(argv)
            # io.input.stream = stream
            # io.input.interactive = interactive

        exit_code = self._run_command(command, io)
        self._running_command = None

        return exit_code

    def _run_command(self, command: Command, io: IO) -> int:
        if self.event_dispatcher is None:
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
            self.event_dispatcher.dispatch(command_event, COMMAND)

            if command_event.command_should_run():
                exit_code = command.run(io)
            else:
                exit_code = ConsoleCommandEvent.RETURN_CODE_DISABLED
        except Exception as e:
            error_event = ConsoleErrorEvent(command, io, e)
            self.event_dispatcher.dispatch(error_event, ERROR)
            error = error_event.error
            exit_code = error_event.exit_code

            if exit_code == 0:
                error = None

        terminate_event = ConsoleTerminateEvent(command, io, exit_code)
        self.event_dispatcher.dispatch(terminate_event, TERMINATE)

        if error is not None:
            raise error

        return terminate_event.exit_code
