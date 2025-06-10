from __future__ import annotations

import pytest

from rich.console import Console


_CONSOLE_KEY = None # pytest.StashKey[Console]

def get_console_key() -> pytest.StashKey[Console]:
    global _CONSOLE_KEY
    if _CONSOLE_KEY is None:
        _CONSOLE_KEY = pytest.StashKey[Console]()

    return _CONSOLE_KEY


def create_console_key(config: pytest.Config) -> Console:
    from baloto.cleo.rich.console_factory import ConsoleFactory

    console_key = get_console_key()
    console = config.stash.get(console_key, None)
    if console is None:
        console = ConsoleFactory.console_output()
        config.stash.setdefault(console_key, console)
    return config.stash.get(console_key, None)




