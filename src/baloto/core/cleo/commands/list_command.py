from __future__ import annotations

from typing import ClassVar

from baloto.core.cleo.commands.command import Command
from core.cleo.io.inputs.argument import Argument


class ListCommand(Command):
    name = "list"

    description = "Lists commands."
