from __future__ import annotations

import argparse
from contextlib import suppress
from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING
from typing import cast

from glom import glom

from baloto.__version__ import __version__
from baloto.cleo.cleo_application import Application as CleoApplication
# from baloto.cleo.decorator import set_rich_console
from baloto.cleo.events.console_events import COMMAND
from baloto.cleo.events.event_dispatcher import EventDispatcher
from baloto.cleo.exceptions.errors import CleoCommandNotFoundError
from baloto.cleo.exceptions.errors import CleoError
from baloto.cleo.io.inputs.argv_input import ArgvInput
from baloto.cleo.io.outputs.console_output import ConsoleOutput
from baloto.cleo.utils import find_similar_names
from baloto.core.utils.helpers import ensure_path, directory
from baloto.miloto.console.commands.command import Command
from baloto.miloto.console.loaders.command_loader import CommandLoader
from baloto.miloto.exceptions.errors import BalotoRuntimeError

if TYPE_CHECKING:
    from collections.abc import Callable
    from baloto.cleo.events.event import Event
    from baloto.cleo.io.inputs.definition import Definition
    from baloto.cleo.io.inputs.input import Input
    from baloto.cleo.io.io import IO
    from baloto.cleo.io.outputs.output import Output
    from baloto.miloto.miloto import Miloto


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


def load_command(name: str) -> Callable[[], Command]:
    def _load() -> Command:
        words = name.split(" ")
        module = import_module("baloto.miloto.console.commands." + ".".join(words))
        command_class = getattr(module, "".join(c.title() for c in words) + "Command")
        command: Command = command_class()
        return command

    return _load

COMMANDS = ["about"]


class Application(CleoApplication):
    def __init__(self, name: str = "console", version: str = "") -> None:
        super().__init__("miloto", __version__)

        self._miloto: Miloto | None = None
        self._io: IO | None = None
        self._working_directory = Path.cwd()
        self._project_directory: Path | None = None
        self._no_ansi: bool | None = None
        self._force_ansi: bool | None = None
        dispatcher = EventDispatcher()
        dispatcher.add_listener(COMMAND, register_command_loggers)
        dispatcher.add_listener(COMMAND, self.flush_screen)
        self.event_dispatcher = dispatcher

        self.set_command_loader(CommandLoader({name: load_command(name) for name in COMMANDS}))

    @property
    def miloto(self) -> Miloto:
        from baloto.miloto.miloto import Miloto

        if self._miloto is not None:
            return self._miloto

        self._miloto = Miloto(cwd=self.project_directory, io=self._io)

        return self._miloto

    @property
    def project_directory(self) -> Path:
        return self._project_directory or self._working_directory

    @property
    def command_loader(self) -> CommandLoader:
        command_loader = self._command_loader
        assert isinstance(command_loader, CommandLoader)
        return command_loader
    
    def default_definition(self) -> Definition:
        from baloto.cleo.io.inputs.option import Option

        definition = super().default_definition()

        definition.add_option(
            Option.make("--dry-run", None, description="Perform all actions except updating files")
        )

        return definition

    def create_io(
        self,
        input: Input | None = None,
        output: Output | None = None,
        error_output: Output | None = None,
    ) -> IO:
        from rich.style import Style
        from baloto.cleo.rich.console_factory import ConsoleFactory

        io = super().create_io(input, output, error_output)

        formatter = io.output.formatter
        formatter.set_style("switch", Style(color="green", italic=True))
        formatter.set_style("command", Style(color="magenta", bold=True))
        formatter.set_style("alias", Style(color="magenta", italic=True, bold=True))
        formatter.set_style("prog", Style(color="medium_orchid3", bold=True))
        formatter.set_style("dark_warning", Style(color="dark_goldenrod", bold=True))
        formatter.set_style("option", Style(color="bright_cyan", bold=True))

        ConsoleOutput.formatter = formatter


        io.output = ConsoleOutput(ConsoleFactory.console_output())
        io.error_output = ConsoleOutput(ConsoleFactory.console_error_output())

        io.output.formatter = formatter
        io.error_output.formatter = formatter
        # set_rich_console(io.output.console)

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

        self._description = glom(self.miloto.poetry.pyproject.data, "project.description")
        self._configure_global_options(io)


        if self._force_ansi and self._no_ansi is None:
            ...

        with directory(self._working_directory):
            exit_code: int = 1

            try:
                exit_code = super()._run(io)
            except BalotoRuntimeError as e:
                io.error_output.write("")
                e.write(io)
                io.error_output.write("")
            except CleoCommandNotFoundError as e:
                command = self._get_command_name(io)

                if command is not None and (message := COMMAND_NOT_FOUND_MESSAGES.get(command)):
                    io.error_output.write("")
                    io.error_output.write(COMMAND_NOT_FOUND_PREFIX_MESSAGE)
                    io.error_output.write("")
                    return 1

                if command is not None and command in self.get_namespaces():
                    sub_commands = []

                    for key in self._commands:
                        if key.startswith(f"{command} "):
                            sub_commands.append(key)

                    io.error_output.write(
                        f"The requested command does not exist in the [command]{command}[/] namespace."
                    )
                    suggested_names = find_similar_names(command, sub_commands)
                    self._error_write_command_suggestions(io, suggested_names, f"#{command}")
                    return 1

                if command is not None:
                    suggested_names = find_similar_names(command, list(self._commands.keys()))
                    io.error_output.write(
                        f"The requested command [command]{command}[/] does not exist."
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
            io.error_output.write(f"\n[error]Did you mean one of these perhaps?[/]{suggestions}")

        io.error_output.write(
            "\n[b]Documentation: [/]" f"[info]https://python-poetry.org/docs/cli/{doc_tag or ''}[/]"
        )

    def _configure_global_options(self, io: IO) -> None:
        self._working_directory = ensure_path(Path.cwd(), is_directory=True)
        self._no_ansi = io.input.option("no-ansi")
        self._force_ansi = io.input.option("ansi")

    def _sort_global_options(self, io: IO) -> None:
        original_input = cast("ArgvInput", io.input)
        # noinspection PyProtectedMember
        tokens: list[str] = original_input._tokens

        parser = argparse.ArgumentParser(add_help=False)


        for option in self.definition.options():
            parser.add_argument(
                f"--{option.name}",
                *([f"-{option.shortcut}"] if option.shortcut else []),
                action="store_true" if option.flag else "store",
            )

        args, remaining_args = parser.parse_known_args(tokens)

        tokens = []
        for option in self.definition.options():
            key = option.name.replace("-", "_")
            value = getattr(args, key, None)

            if value is not None:
                if value:  # is truthy
                    tokens.append(f"--{option.name}")

                if option.accepts_value:
                    tokens.append(str(value))

        sorted_input = ArgvInput([self.name or "", *tokens, *remaining_args])

        with suppress(CleoError):
            sorted_input.bind(self.definition)

        io.input = sorted_input

    def _configure_io(self, io: IO) -> None:
        self._sort_global_options(io)
        super()._configure_io(io)

    def flush_screen(self, event: Event, event_name: str, _: EventDispatcher) -> None:
        self._io.output.clear()



def register_command_loggers(event: Event, event_name: str, _: EventDispatcher) -> None: ...


def main() -> int:
    exit_code: int = Application().run()
    return exit_code


if __name__ == "__main__":
    main()

