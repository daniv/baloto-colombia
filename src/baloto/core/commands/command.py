from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING
from typing import Any
from typing import ClassVar

from baloto.core.cleo.commands.command import Command as CleoCommand
from baloto.core.cleo.exceptions import CleoValueError
from baloto.core.cleo.io.io import IO

if TYPE_CHECKING:
    from baloto.core.application import Application
    from baloto.core.poetry.poetry import Poetry


class Command(CleoCommand, ABC):
    loggers: ClassVar[list[str]] = []
    _poetry: Poetry | None = None

    @property
    def poetry(self) -> Poetry:
        if self._poetry is None:
            return self.get_application().poetry

        return self._poetry

    @poetry.setter
    def poetry(self, poetry: Poetry) -> None:
        self._poetry = poetry

    def interact(self, io: IO) -> None:
        pass

    def handle(self) -> int:
        pass

    def get_application(self) -> Application:
        from baloto.core.application import Application

        application = self.application
        assert isinstance(application, Application)
        return application

    def option(self, name: str, default: Any = None) -> Any:
        try:
            return super().option(name)
        except CleoValueError:
            return default
