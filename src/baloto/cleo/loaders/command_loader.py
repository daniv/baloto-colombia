from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from baloto.cleo.commands.command import Command


class CommandLoader(ABC):
    @property
    @abstractmethod
    def names(self) -> list[str]:
        """
        All registered command names.
        """
        raise NotImplementedError

    @abstractmethod
    def get(self, name: str) -> Command:
        """
        Loads a command.
        """
        raise NotImplementedError

    @abstractmethod
    def has(self, name: str) -> bool:
        """
        Checks whether a command exists or not.
        """
        raise NotImplementedError
