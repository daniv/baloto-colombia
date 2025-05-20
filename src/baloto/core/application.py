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

from core.__version__ import __version__
from core.loaders.command_loader import CommandLoader
from core.loaders.command_loader import load_command
from core.utils.helpers import directory
from core.utils.helpers import ensure_path
from core.commands.command import Command

if TYPE_CHECKING:
    from collections.abc import Callable

    from cleo.events.event import Event
    from cleo.io.inputs.definition import Definition
    from cleo.io.inputs.input import Input
    from cleo.io.outputs.output import Output
    from cleo.io.io import IO

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


def register_command_loggers(event: Event, event_name: str, _: EventDispatcher) -> None: ...
