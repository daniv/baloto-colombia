# Project : baloto-colombia
# File Name : traceback.py
# Dir Path : tests/plugins
# Created on: 2025–06–05 at 22:42:10.

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from rich.traceback import LOCALS_MAX_LENGTH, LOCALS_MAX_STRING

if TYPE_CHECKING:
    pass

__all__ = ("PLUGIN_NAME", )

PLUGIN_NAME = "miloto-traceback"

@pytest.hookimpl
def pytest_addoption(parser: pytest.Parser, pluginmanager: pytest.PytestPluginManager) -> None:
    group = parser.getgroup("tracebacks", "Configuration for displaying rich-tracebacks", after="miloto")

    group.addoption(
        "--tracebacks-code-width",
        metavar="num",
        action="store",
        type=int,
        dest="tracebacks_code_width",
        default=100,
        help="Number of code characters used to render tracebacks, or None for full width. Defaults to %(default)s.",
    )

    group.addoption(
        "--tracebacks-width",
        metavar="num",
        action="store",
        type=int,
        dest="tracebacks_width",
        default=None,
        help="Number of characters used to render tracebacks, or None for full width. Defaults to %(default)s.",
    )

    group.addoption(
        "--tracebacks-extra-lines",
        metavar="num",
        action="store",
        type=int,
        dest="tracebacks_extra_lines",
        default=3,
        help="Additional lines of code to render tracebacks, or None for full width. Defaults is %(default)s.",
    )

    group.addoption(
        "--tracebacks-theme",
        type=str,
        default="ansi_dark",
        help="Override pygments theme used in traceback. Defaults to '%(default)s'",
        dest="tracebacks_theme",
    )

    group.addoption(
        "--tracebacks-word-wrap",
        action="store_false",
        dest="tracebacks_word_wrap",
        help="Enable word wrapping of long tracebacks lines. Defaults to %(default)s."
    )

    group.addoption(
        "--tracebacks-show-locals",
        action="store_true",
        dest="tracebacks_show_locals",
        help="Enable display of locals in tracebacks. Defaults to %(default)s."
    )

    group.addoption(
        "--locals-max-length",
        metavar="num",
        action="store",
        type=int,
        dest="tracebacks_locals_max_length",
        default=LOCALS_MAX_LENGTH,
        help="Maximum length of containers before abbreviating, Defaults to %(default)s.",
    )

    group.addoption(
        "--locals-max-string",
        metavar="num",
        action="store",
        type=int,
        dest="tracebacks_locals_max_string",
        default=LOCALS_MAX_STRING,
        help="Maximum length of string before truncating, Defaults to %(default)s.",
    )

    parser.addini(
        "tracebacks_suppress", type="args", help="Optional sequence of modules or paths to exclude from traceback.", default=())

    group.addoption(
        "--locals-hide-dunder",
        action="store_false",
        dest="tracebacks_locals_hide_dunder",
        help="Hide locals prefixed with double underscore. Defaults to %(default)s"
    )

    group.addoption(
        "--locals-hide-sunder",
        action="store_true",
        dest="tracebacks_locals_hide_sunder",
        help="Hide locals prefixed with single underscore. Defaults to %(default)s."
    )

    group.addoption(
        "--tracebacks-indent-guides",
        action="store_false",
        dest="tracebacks_indent_guides",
        help="Enable indent guides in code and locals. Defaults to %(default)s."
    )

    group.addoption(
        "--tracebacks-max-frames",
        metavar="num",
        action="store",
        type=int,
        dest="tracebacks_max_frames",
        default=100,
        help="Optional maximum number of frames returned by traceback. Default to %(default)s",
    )

def pytest_configure(config: pytest.Config) -> None:
    ...