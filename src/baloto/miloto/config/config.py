# - Project   : baloto-colombia
# - User Naem : solma
# - File Name : config.py
# - Dir Path  : src/baloto/miloto/config
# - Created on: 2025-05-30 at 15:16:43

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    pass

__all__ = ()


class MilitoConfigDict(TypedDict, total=False):
    title: str | None