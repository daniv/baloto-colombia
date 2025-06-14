# Project : baloto-colombia
# File Name : __init__.py
# Dir Path : src/baloto/core/rich/tracebacks
# Created on: 2025–06–13 at 21:49:57.

from __future__ import annotations

from dataclasses import dataclass
from types import TracebackType
from typing import Any
from typing import Generic
from typing import TYPE_CHECKING
from typing import Type
from typing import TypeVar

if TYPE_CHECKING:
    pass

__all__ = ("SysExceptionInfo",)


E = TypeVar("E", bound=BaseException, covariant=True)


@dataclass
class SysExceptionInfo(Generic[E]):
    exc_type: Type[Any]
    exc_value: BaseException
    traceback: TracebackType | None
