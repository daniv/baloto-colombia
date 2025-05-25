from __future__ import annotations

import io
from typing import Generator

import pytest
from rich.console import Console


@pytest.fixture
def string_io() -> io.StringIO:
    return io.StringIO()

@pytest.fixture(scope="function")
def terminal_string_io_console(string_io: io.StringIO) -> Generator[Console, None, None]:
      console = Console(file=string_io, force_terminal = True)
      yield console
      console.quiet = True
      console.file = None
