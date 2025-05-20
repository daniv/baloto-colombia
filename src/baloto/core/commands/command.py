from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import ClassVar

from baloto.core.cleo.commands.command import Command as CleoCommand
from core.cleo.exceptions import CleoValueError

if TYPE_CHECKING:
    from miloto.application import Application


class Command(CleoCommand):
    loggers: ClassVar[list[str]] = []
