# - Project   : baloto-colombia
# - User Naem : solma
# - File Name : command.py
# - Dir Path  : src/baloto/miloto/commands
# - Created on: 2025-05-30 at 22:45:05

from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, ClassVar, IO, Any

from baloto.cleo.commands.cleo_command import Command as CleoCmmand
from baloto.cleo.exceptions.errors import CleoValueError
from baloto.miloto.miloto import Miloto

if TYPE_CHECKING:
    from baloto.cleo.cleo_application import Application


class Command(CleoCmmand, ABC):
    loggers: ClassVar[list[str]] = []

    _miloto: Miloto | None = None
    # _poetry: Poetry | None = None

    @property
    def miloto(self) -> Miloto:
        if self._miloto is None:
            return self.get_application().poetry

        return self._miloto

    @miloto.setter
    def miloto(self, miloto: Miloto) -> None:
        self._miloto = miloto

    def interact(self, io: IO) -> None:
        pass

    def handle(self) -> int:
        pass

    def get_application(self) -> Application:
        from baloto.cleo.cleo_application import Application

        application = self.application
        assert isinstance(application, Application)
        return application

    def option(self, name: str, default: Any = None) -> Any:
        try:
            return super().option(name)
        except CleoValueError:
            return default

