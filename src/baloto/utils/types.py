# - Project   : baloto-colombia
# - User Naem : solma
# - File Name : types.py
# - Dir Path  : src/baloto/utils
# - Created on: 2025-05-30 at 17:32:49

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic_extra_types.pendulum_dt import DateTime, Date

if TYPE_CHECKING:
    pass

__all__ = ("StrIntFloat", "OptionalStrIntFloat", "OptionalBool", "OptionalStr", "OptionalInt", "OptionalIntFloat", "OptionalAny", "OptionalBool", "DictStrStr")


StrIntFloat = str | int | float
OptionalStrIntFloat = StrIntFloat | None
OptionalBool = bool | None
OptionalStr = str | None
OptionalInt = int | None
OptionalIntFloat = OptionalInt, float
OptionalDate = Date | None
OptionalDateTime = DateTime | None
DictStrAny = dict[str, Any]
DictStrStr = dict[str | str]
DictAny = dict[Any, Any]
SetStr = list[str]
ListStr = list[str]
ListInt = list[int]
ListStrIntFloat = list[StrIntFloat]
IntStr = int | str
OptionalAny = Any | None