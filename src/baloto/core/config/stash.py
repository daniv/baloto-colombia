# Project : baloto-colombia
# File Name : stash.py
# Dir Path : src/baloto/core/config
# Created on: 2025–06–13 at 21:26:35.

from __future__ import annotations

from typing import Any
from typing import Generic
from typing import TYPE_CHECKING
from typing import TypeVar
from typing import cast

if TYPE_CHECKING:
    pass

__all__ = ("RichStash",)


T = TypeVar("T")
D = TypeVar("D")


class RichStashKey(Generic[T]):
    __slots__ = ()


class RichStash:
    __slots__ = ("_storage",)

    def __init__(self) -> None:
        self._storage: dict[RichStashKey[Any], object] = {}

    def __setitem__(self, key: RichStashKey[T], value: T) -> None:
        self._storage[key] = value

    def __getitem__(self, key: RichStashKey[T]) -> T:
        return cast(T, self._storage[key])

    def get(self, key: RichStashKey[T], default: D) -> T | D:
        try:
            return self[key]
        except KeyError:
            return default

    def setdefault(self, key: RichStashKey[T], default: T) -> T:
        try:
            return self[key]
        except KeyError:
            self[key] = default
            return default

    def __delitem__(self, key: RichStashKey[T]) -> None:
        del self._storage[key]

    def __contains__(self, key: RichStashKey[T]) -> bool:
        return key in self._storage

    def __len__(self) -> int:
        return len(self._storage)
