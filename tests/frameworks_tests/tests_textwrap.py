# Project : baloto-colombia
# File Name : tests_textwrap.py
# Dir Path : tests/frameworks_tests
# Created on: 2025–06–16 at 12:14:23.

from __future__ import annotations

import textwrap
from typing import TYPE_CHECKING
from typing import Sized
from typing import TypeVar
import pytest
from pytest import param
from hamcrest import assert_that
from hamcrest import equal_to

from baloto.cleo.io.buffered_io import BufferedIO
from baloto.cleo.io.stream_io import StreamIO

if TYPE_CHECKING:
    pass

parameterize = pytest.mark.parametrize
SizedT = TypeVar("SizedT", bound=Sized)

LOREM =  (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut "
    "labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco "
)

def test_template(stream_io: StreamIO) -> None:
    shorten20 = textwrap.shorten(LOREM, 20)
    shorten30 = textwrap.shorten(LOREM, 30)
    if stream_io:
        stream_io.output.line()
        stream_io.output.write("20: ", shorten20, new_line_start=True)
        stream_io.output.write("30: ", shorten30, new_line_start=True)
