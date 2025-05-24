from __future__ import annotations

import argparse
import sys
from contextlib import suppress
from pathlib import Path
from typing import TYPE_CHECKING
from typing import cast

from baloto.core.cleo.application import Application as CleoApplication
from baloto.core.cleo.events.console_events import COMMAND
from baloto.core.cleo.events.event_dispatcher import EventDispatcher
from baloto.core.cleo.exceptions import CleoCommandNotFoundError
from baloto.core.cleo.exceptions import CleoError
from baloto.core.cleo.formatters.formatter import Formatter
from baloto.core.cleo.io.inputs.argv_input import ArgvInput
from baloto.core.cleo.io.outputs.console_output import ConsoleOutput
from baloto.core.cleo.utils import find_similar_names
from baloto.core.exceptions import BalotoRuntimeError
from baloto.core.utils.helpers import directory
from baloto.core.utils.helpers import ensure_path

if TYPE_CHECKING:
    from baloto.core.cleo.events.event import Event
    from baloto.core.cleo.io.inputs.definition import Definition
    from baloto.core.cleo.io.inputs.input import Input
    from baloto.core.cleo.io.outputs.output import Output
    from baloto.core.cleo.io.io import IO
    from baloto.core.poetry.poetry import Poetry
    from rich.console import Console

COMMAND_NOT_FOUND_PREFIX_MESSAGE = (
    "Looks like you're trying to use a {application_name} command that is not available."
)
COMMAND_NOT_FOUND_MESSAGES = {
    "shell": """
Since <info>Poetry (<b>2.0.0</>)</>, the <c1>shell</> command is not installed by default. You can use,

  - the new <c1>env activate</> command (<b>recommended</>); or
  - the <c1>shell plugin</> to install the <c1>shell</> command

<b>Documentation:</> https://python-poetry.org/docs/managing-environments/#activating-the-environment

<warning>Note that the <c1>env activate</> command is not a direct replacement for <c1>shell</> command.
"""
}


class Application(CleoApplication):
    def __init__(self, name: str = "console", version: str = "") -> None:
        super().__init__(name, version)

        self._io: IO | None = None
        self._poetry: Poetry | None = None
        self._working_directory = Path.cwd()
        self._project_directory: Path | None = None
        self._console: Console | None = None
        self._error_console: Console | None = None
        dispatcher = EventDispatcher()
        dispatcher.add_listener(COMMAND, register_command_loggers)
        dispatcher.add_listener(COMMAND, self.flush_screen)
        self.event_dispatcher = dispatcher

    @property
    def project_directory(self) -> Path:
        return self._project_directory or self._working_directory

    @property
    def poetry(self) -> Poetry:
        from baloto.core.poetry.poetry import Poetry

        if self._poetry is not None:
            return self._poetry

        self._poetry = Poetry.create_poetry(cwd=self.project_directory, io=self._io)

        return self._poetry

    # @property
    # def console(self) -> Console:
    #     if self._console is None:
    #         self._console = getattr(self._io.output, "console")
    #     return self._console
    #
    # @property
    # def error_console(self) -> Console:
    #     if self._error_console is None:
    #         self._error_console = getattr(self._io.error_output, "console")
    #     return self._error_console

    @property
    def _default_definition(self) -> Definition:
        from baloto.core.cleo.io.inputs.option import Option

        definition = super()._default_definition

        definition.add_option(
            Option("--dry-run", None, description="Perform all actions except updating files")
        )

        # definition.add_option(
        #     Option(
        #         "--project",
        #         "-P",
        #         flag=False,
        #         description=(
        #             "Specify another path as the project root."
        #             " All command-line arguments will be resolved relative to the current working directory."
        #         ),
        #     )
        # )
        #
        # definition.add_option(
        #     Option(
        #         "--directory",
        #         "-C",
        #         flag=False,
        #         description=(
        #             "The working directory for the Poetry command (defaults to the"
        #             " current working directory). All command-line arguments will be"
        #             " resolved relative to the given directory."
        #         ),
        #     )
        # )

        return definition

    def create_io(
        self,
        input: Input | None = None,
        output: Output | None = None,
        error_output: Output | None = None,
    ) -> IO:
        io = super().create_io(input, output, error_output)

        from rich.style import Style
        from rich.console import Console

        formatter = Formatter()
        formatter.set_style("switch", Style(color="green", italic=True))
        formatter.set_style("prog", Style(color="medium_orchid3", bold=True))
        formatter.set_style("dark_warning", Style(color="dark_goldenrod", bold=True))
        core_theme = formatter.create_theme()

        console = Console(theme=core_theme, file=sys.stdout, force_interactive=True, soft_wrap=True)
        err_console = Console(theme=core_theme, stderr=True, style="error", soft_wrap=True)
        io.output = ConsoleOutput(console)
        io.error_output = ConsoleOutput(err_console)

        self._io = io

        """

        self.set_style("question", Style("cyan"))
        self.set_style("c1", Style("cyan"))
        self.set_style("c2", Style("default", options=["bold"]))
        self.set_style("b", Style("default", options=["bold"]))
                formatter.set_style("c1", Style("cyan"))
        formatter.set_style("c2", Style("default", options=["bold"]))
        formatter.set_style("comment", Style("green"))
        formatter.set_style("success", Style("green"))

        # Dark variants
        formatter.set_style("c1_dark", Style("cyan", options=["dark"]))
        formatter.set_style("c2_dark", Style("default", options=["bold", "dark"]))
        formatter.set_style("success_dark", Style("green", options=["dark"]))
        dark_colors = ["black", "red", "green", "yellow", "blue",
               "magenta", "cyan", "gray"]
light_colors = ["brightblack", "brightred", "brightgreen", "brightyellow", "brightblue",
                "brightmagenta", "brightcyan", "white"]
        """
        return io
        #
        # miloto_theme = Theme(
        #     {
        #         "error": Style(color="red", bold=True),
        #         "warning": Style(color="dark_goldenrod", bold=True),
        #         "info": Style(color="blue", bold=False),
        #         "debug": Style(bold=False, dim=True),
        #
        #         "switch": Style(color="green", bold=True),
        #         "option": Style(color="bright_cyan", bold=True),
        #         "debug.option": Style(color="bright_cyan", bold=True, italic=True),
        #         "debug.argument": Style(color="bright_magenta", bold=True, italic=True),
        #         "argument": Style(color="bright_magenta", bold=True),
        #         "command": Style(color="magenta", bold=True),
        #         "prog": Style(color="medium_orchid3", bold=True),
        #         "money": Style(color="green3", bold=True),
        #         "report": Style(bold=True, italic=True),
        #         "date": Style(color="green", italic=True),
        #
        #         "help.var": Style(color="gray58", italic=True),
        #         "cmd.class": Style(italic=True, color="bright_cyan"),
        #         "cmd.def": Style(italic=True, color="bright_cyan"),
        #         "cmd.callable": Style(italic=True, color="bright_cyan"),
        #         "cmd.var": Style(italic=True, color="bright_cyan"),
        #         "debug.hex": Style(italic=True, color="green_yellow"),
        #     }
        # )

    def _run(self, io: IO) -> int:
        # we do this here and not inside the _configure_io implementation in order
        # to ensure the users are not exposed to a stack trace for providing invalid values to
        # the options --directory or --project, configuring the options here allow cleo to trap and
        # display the error cleanly unless the user uses verbose or debug
        self._description = self.poetry.get_project().get("description", "")
        self._configure_global_options(io)

        with directory(self._working_directory):
            exit_code: int = 1

            try:
                exit_code = super()._run(io)
            except BalotoRuntimeError as e:
                io.write_error("")
                e.write(io)
                io.write_error("")
            except CleoCommandNotFoundError as e:
                command = self._get_command_name(io)

                if command is not None and (message := COMMAND_NOT_FOUND_MESSAGES.get(command)):
                    io.write_error("")
                    io.write_error(COMMAND_NOT_FOUND_PREFIX_MESSAGE)
                    io.write_error(message)
                    return 1

                if command is not None and command in self.get_namespaces():
                    sub_commands = []

                    for key in self._commands:
                        if key.startswith(f"{command} "):
                            sub_commands.append(key)

                    io.write_error(
                        f"The requested command does not exist in the [command]{command}[/] namespace."
                    )
                    suggested_names = find_similar_names(command, sub_commands)
                    self._error_write_command_suggestions(io, suggested_names, f"#{command}")
                    return 1

                if command is not None:
                    suggested_names = find_similar_names(command, list(self._commands.keys()))
                    io.write_error(
                        f"[c2]The requested command [command]{command}[/] does not exist.[/]"
                    )
                    self._error_write_command_suggestions(io, suggested_names)
                    return 1

                raise e

        return exit_code

    def _error_write_command_suggestions(
        self, io: IO, suggested_names: list[str], doc_tag: str | None = None
    ) -> None:
        if suggested_names:
            suggestion_lines = [
                f"[c1]{name.replace(' ', '[/] [b]', 1)}[/]: {self._commands[name].description}"
                for name in suggested_names
            ]
            suggestions = "\n    ".join(["", *sorted(suggestion_lines)])
            io.write_error(f"\nDid you mean one of these perhaps?{suggestions}")

        io.write_error(
            "\n[b]Documentation: [/]" f"[info]https://python-poetry.org/docs/cli/{doc_tag or ''}[/]"
        )

    def _configure_global_options(self, io: IO) -> None:
        """
        Configures global options for the application by setting up the relevant
        directories, disabling plugins or cache, and managing the working and
        project directories. This method ensures that all directories are valid
        paths and handles the resolution of the project directory relative to the
        working directory if necessary.

        :param io: The IO instance whose input and options are being read.
        :return: Nothing.
        """
        # we use ensure_path for the directories to make sure these are valid paths
        # this will raise an exception if the path is invalid
        self._working_directory = ensure_path(Path.cwd(), is_directory=True)

        # self._project_directory = io.input.option("project")
        # if self._project_directory is not None:
        #     self._project_directory = Path(self._project_directory)
        #     self._project_directory = ensure_path(
        #         self._project_directory
        #         if self._project_directory.is_absolute()
        #         else self._working_directory.joinpath(self._project_directory).resolve(
        #             strict=False
        #         ),
        #         is_directory=True,
        #     )

    def _sort_global_options(self, io: IO) -> None:
        """
        Sorts global options of the provided IO instance according to the
        definition of the available options, reordering and parsing arguments
        to ensure consistency in input handling.

        The function interprets the options and their corresponding values
        using an argument parser, constructs a sorted list of tokens, and
        recreates the input with the rearranged sequence while maintaining
        compatibility with the initially provided input stream.

        If using in conjunction with `_configure_run_command`, it is recommended that
        it be called first in order to correctly handling cases like
        `poetry run -V python -V`.

        :param io: The IO instance whose input and options are being processed
                   and reordered.
        :return: Nothing.
        """
        original_input = cast("ArgvInput", io.input)
        # noinspection PyProtectedMember
        tokens: list[str] = original_input._tokens

        parser = argparse.ArgumentParser(add_help=False)

        for option in self.definition.options:
            parser.add_argument(
                f"--{option.name}",
                *([f"-{option.shortcut}"] if option.shortcut else []),
                action="store_true" if option.is_flag() else "store",
            )

        args, remaining_args = parser.parse_known_args(tokens)

        tokens = []
        for option in self.definition.options:
            key = option.name.replace("-", "_")
            value = getattr(args, key, None)

            if value is not None:
                if value:  # is truthy
                    tokens.append(f"--{option.name}")

                if option.accepts_value():
                    tokens.append(str(value))

        sorted_input = ArgvInput([self._name or "", *tokens, *remaining_args])

        # this is required to ensure stdin is transferred
        sorted_input.stream = original_input.stream

        # this is required as cleo internally checks for `io.input._interactive`
        # when configuring io, and cleo's test applications overrides this attribute
        # explicitly causing test setups to fail
        sorted_input.interactive = io.input.interactive

        with suppress(CleoError):
            sorted_input.bind(self.definition)

        io.input = sorted_input

    def _configure_io(self, io: IO) -> None:
        self._sort_global_options(io)
        super()._configure_io(io)

    def flush_screen(self, event: Event, event_name: str, _: EventDispatcher) -> None:
        self._io.console.clear(home=True)


def register_command_loggers(event: Event, event_name: str, _: EventDispatcher) -> None: ...
