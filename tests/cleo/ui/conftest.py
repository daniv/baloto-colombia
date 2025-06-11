# Project : baloto-colombia
# File Name : conftest.py
# Dir Path : tests/cleo/ui
# Created on: 2025–06–07 at 14:55:16.

from __future__ import annotations

from io import StringIO
from typing import Callable
from typing import Generator
from typing import TYPE_CHECKING

import pytest

from baloto.cleo.io.buffered_io import BufferedIO
from baloto.cleo.io.stream_io import StreamIO
from baloto.cleo.io.inputs.string_input import StringInput

if TYPE_CHECKING:
    pass


@pytest.fixture()
def buffered_io() -> BufferedIO:
    input_ = StringInput("")
    input_.stream = StringIO()
    return BufferedIO(input_)


@pytest.fixture()
def stream_io() -> StreamIO:
    return StreamIO()
