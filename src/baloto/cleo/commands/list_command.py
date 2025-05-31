from __future__ import annotations

from typing import ClassVar

from baloto.cleo.commands.cleo_command import Command as CleoCommand
from baloto.cleo.io.inputs.argument import Argument


class ListCommand(CleoCommand):
    name = "list"

    description = "Lists commands."

    help = """\
    
The {script_name} [command]{command_name}[/command] command lists all commands:
  >>> [command]{command_full_name}[/command]

You can also display the commands for a specific namespace:
  >>> [command]{command_full_name} test[/command]
"""

    arguments: ClassVar[list[Argument]] = [Argument.make("namespace", required=False, description="The namespace name")]

    def handle(self) -> int:
        from baloto.cleo.descriptors.text_descriptor import TextDescriptor

        TextDescriptor().describe(self._io, self.application, namespace=self.argument("namespace"))

        return 0
