# Project : baloto-colombia
# File Name : tests_textwrap.py
# Dir Path : tests/cleo_tests/formatters
# Created on: 2025–06–16 at 03:58:39.

from __future__ import annotations

from typing import TYPE_CHECKING

from baloto.cleo.io.stream_io import StreamIO

if TYPE_CHECKING:
    pass

text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt"
def test_shorten(stream_io: StreamIO) -> None:
    i = 0