# - Project   : baloto-colombia
# - User Naem : solma
# - File Name : __init__.py
# - Dir Path  : src/baloto/utils
# - Created on: 2025-05-30 at 15:58:51

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

__all__ = ("is_pydevd_mode", "is_debug_mode")


def is_pydevd_mode() -> bool:
    pydevd = sys.modules.get("pydevd")
    return pydevd is not None


def is_debug_mode() -> bool:
    get_trace = getattr(sys, "gettrace", None)
    return False if get_trace is None else True