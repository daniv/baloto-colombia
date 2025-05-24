from __future__ import annotations

import dataclasses
import json

from abc import ABC
from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import Any

from baloto.core.cleo.io.null_io import NullIO


if TYPE_CHECKING:
    from baloto.core.cleo.io.io import IO

UNSET = object()


class PropertyNotFoundError(ValueError):
    pass


class ConfigSource(ABC):
    @abstractmethod
    def get_property(self, key: str) -> Any: ...

    @abstractmethod
    def add_property(self, key: str, value: Any) -> None: ...

    @abstractmethod
    def remove_property(self, key: str) -> None: ...

    @abstractmethod
    def has_property(self, key: str) -> bool: ...
