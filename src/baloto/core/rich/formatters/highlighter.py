# Project : baloto-colombia
# File Name : highlighter.py
# Dir Path : src/baloto/core/rich/formatters
# Created on: 2025–06–14 at 01:03:30.

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.highlighter import ReprHighlighter

if TYPE_CHECKING:
    pass

__all__ = ("BalotoHighlighter",)


class BalotoHighlighter(ReprHighlighter):
    def __init__(self):
        self.highlights.append(
            r"\b(?P<exception>AssertionError|KeyError|AttributeError|Exception|RuntimeError|IOError|SyntaxError|FileNotFoundError|FileExistsError|TypeError|NotImplementedError|ValueError|BaseException|ModuleNotFoundError|KeyboardInterrupt|IndexError)\b",
        )
        self.highlights.append(r"(?P<dim>.*/)(?P<bold>.+)")
