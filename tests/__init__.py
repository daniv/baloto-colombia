from __future__ import annotations

import pytest
from rich.console import Console

_CONSOLE_KEY = None # pytest.StashKey[Console]

def get_console_key() -> pytest.StashKey[Console]:
    global _CONSOLE_KEY
    if _CONSOLE_KEY is None:
        _CONSOLE_KEY = pytest.StashKey[Console]()

    return _CONSOLE_KEY