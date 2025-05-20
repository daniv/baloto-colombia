from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING
from typing import Any
from typing import ClassVar

from baloto.core.cleo.commands.command import Command as CleoCommand
from baloto.core.cleo.exceptions import CleoValueError
<<<<<<< HEAD
=======
from baloto.core.cleo.io.io import IO
>>>>>>> 7b57a141afe8f99f7baeb1f96d0ea8f96a2b0fe5

if TYPE_CHECKING:
    from baloto.core.application import Application
    from baloto.core.poetry import Poetry


class Command(CleoCommand, ABC):
    loggers: ClassVar[list[str]] = []
    _poetry: Poetry | None = None

    @property
    def poetry(self) -> Poetry:
        if self._poetry is None:
            return self.application.poetry

        return self._poetry

    @poetry.setter
    def poetry(self, poetry: Poetry) -> None:
        self._poetry = poetry

<<<<<<< HEAD
=======
    def interact(self, io: IO) -> None:
        pass

    def handle(self) -> int:
        pass

>>>>>>> 7b57a141afe8f99f7baeb1f96d0ea8f96a2b0fe5
    @property
    def application(self) -> Application:
        from baloto.core.application import Application

        application = self.application
        assert isinstance(application, Application)
        return application

    def option(self, name: str, default: Any = None) -> Any:
        try:
            return super().option(name)
        except CleoValueError:
<<<<<<< HEAD
            return default
=======
            return default

>>>>>>> 7b57a141afe8f99f7baeb1f96d0ea8f96a2b0fe5
