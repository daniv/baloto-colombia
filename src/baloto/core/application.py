from __future__ import annotations

import argparse
import logging

from contextlib import suppress
from importlib import import_module
from pathlib import Path
from typing import TYPE_CHECKING
from typing import cast

from cleo.application import Application as BaseApplication
from cleo.utils import find_similar_names
from cleo.application import Application as CleoApplication
from cleo.events.console_command_event import ConsoleCommandEvent
from cleo.events.console_events import COMMAND
from cleo.events.event_dispatcher import EventDispatcher
from cleo.exceptions import CleoCommandNotFoundError
from cleo.exceptions import CleoError

# from cleo.formatters.style import Style
from cleo.io.inputs.argv_input import ArgvInput

from baloto.core.__version__ import __version__
from baloto.core.loaders.command_loader import CommandLoader
from baloto.core.loaders.command_loader import load_command
from baloto.core.utils.helpers import directory
from baloto.core.utils.helpers import ensure_path
from baloto.core.commands.command import Command

if TYPE_CHECKING:
    from collections.abc import Callable

    from cleo.events.event import Event
    from cleo.io.inputs.definition import Definition
    from cleo.io.inputs.input import Input
    from cleo.io.outputs.output import Output
    from cleo.io.io import IO
    from baloto.core.poetry import Poetry

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
        self._working_directory = Path.cwd()
        self._project_directory: Path | None = None
        dispatcher = EventDispatcher()
        dispatcher.add_listener(COMMAND, register_command_loggers)
        self.event_dispatcher = dispatcher

    @property
    def _default_definition(self) -> Definition:
        from baloto.core.cleo.io.inputs.option import Option

        definition = super()._default_definition

        definition.add_option(
            Option(
                "--project",
                "-P",
                flag=False,
                description=(
                    "Specify another path as the project root."
                    " All command-line arguments will be resolved relative to the current working directory."
                ),
            )
        )

        definition.add_option(
            Option(
                "--directory",
                "-C",
                flag=False,
                description=(
                    "The working directory for the Poetry command (defaults to the"
                    " current working directory). All command-line arguments will be"
                    " resolved relative to the given directory."
                ),
            )
        )

        return definition


def register_command_loggers(event: Event, event_name: str, _: EventDispatcher) -> None: ...
