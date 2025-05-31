from __future__ import annotations

from typing import ClassVar

from baloto.cleo.commands.cleo_command import Command as CleoCommand
from baloto.cleo.io.inputs.argument import Argument


class HelpCommand(CleoCommand):
    name = "help"

    description = "Displays help for a command."

    arguments: ClassVar[list[Argument]] = [
        Argument.make(
            "commandname",
            required=False,
            description="The command name",
            default="help",
        )
    ]

    help = """\
The [command]{command_name}[/] command displays help for a given command:

  [command]{command_full_name} list[/]

To display the list of available commands, please use the [command]list[/command] command.
"""
    _command = None

    def set_command(self, command: CleoCommand) -> None:
        self._command = command

    def configure(self) -> None:
        self.ignore_validation_errors = True

        super().configure()

    def handle(self) -> int:
        from baloto.cleo.descriptors.text_descriptor import TextDescriptor

        if self._command is None:
            assert self._application is not None
            self._command = self._application.find(self.argument("commandname"))

        console = getattr(self.io.output, "console")
        console.line(1)
        descriptor = TextDescriptor()
        descriptor.describe(self._io, self._application, title=True)
        descriptor.describe(self._io, self._command)

        self._command = None

        return 0
