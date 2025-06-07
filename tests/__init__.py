from __future__ import annotations

import pytest

from baloto.cleo.io.outputs.console_output import ConsoleOutput

_CONSOLE_OUTPUT_KEY = None # pytest.StashKey[Console]

def get_console_output_key() -> pytest.StashKey[ConsoleOutput]:
    global _CONSOLE_OUTPUT_KEY
    if _CONSOLE_OUTPUT_KEY is None:
        _CONSOLE_OUTPUT_KEY = pytest.StashKey[ConsoleOutput]()

    return _CONSOLE_OUTPUT_KEY