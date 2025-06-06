# — Project : baloto-colombia
# — File Name : plugin.py
# — Dir Path : tests/plugins/logger
# — Created on: 2025–06–04 at 20:01:17.

from __future__ import annotations

import argparse
import logging
from typing import TYPE_CHECKING, Any, Iterable

import pytest
from pydantic import BaseModel, ConfigDict
from rich.console import Console



if TYPE_CHECKING:
    pass

PLUGIN_NAME = "Logger Plugin"

__all__ = ()



@pytest.hookimpl
def pytest_addhooks(pluginmanager: pytest.PytestPluginManager) -> None:
    ...

@pytest.hookimpl
def pytest_addoption(parser: pytest.Parser, pluginmanager: pytest.PytestPluginManager) -> None:
    group = parser.getgroup("miloto logging")

    def add_option_ini(*opts: Iterable[str], dest, default: Any = None, type=None, **kwargs):
        parser.addini(
            dest, default=default, type=type, help="Default value for " + str(opts[0])
        )
        group.addoption(*opts, dest=dest, default=default, **kwargs)

    add_option_ini(
        "--log-rich-level",
        dest="log_rich_level",
        default=logging.NOTSET,
        metavar="LEVEL",
        help=(
            "Level of messages to catch/display."
            " Not set by default, so it depends on the root/parent log handler's"
            ' effective level, where it is "WARNING" by default.'
        ),
    )
    add_option_ini(
        "--log-rich-format",
        metavar="FORMAT",
        dest="log_rich_format",
        default="%(message)s",
        help="Log format used by the logging module",
    )
    add_option_ini(
        "--log-rich-date-fmt",
        metavar="DATE_FORMAT",
        dest="log_rich_date_fmt",
        default="[%X]",
        help="Log date format used by the logging module",
    )
    group.addoption(
        "--show-time",
        action="store_true",
        dest="log_rich_show_time",
        help="Show a column for the time. Defaults to True."
    )
    group.addoption(
        "--omit-repeated",
        action="store_true",
        dest="log_rich_omit_repeated_times",
        help="Omit repetition of the same time. Defaults to True."
    )
    group.addoption(
        "--show-level",
        action="store_true",
        dest="log_rich_show_level",
        help="Show a column for the level. Defaults to True."
    )
    group.addoption(
        "--show-path",
        action="store_true",
        dest="log_rich_show_path",
        help="Show the path to the original log call. Defaults to True."
    )
    group.addoption(
        "--enable-link-path",
        action="store_true",
        dest="log_rich_enable_link_path",
        help="Show the path to the original log call. Defaults to True."
    )
    group.addoption(
        '--highlighter',
        action=StoreHighlighter,
        default=None,
        dest="log_rich_highlighter",
        # default="ReprHighlighter",
        metavar='TYPE',
        type=validate_highlighter,
        help='Highlighter to style log messages, Defaults to use ReprHighlighter.',
    )
    group.addoption(
        "--markup",
        action="store_false",
        dest="log_rich_markup",
        help="Enable console markup in log messages. Defaults to False."
    )
    group.addoption(
        "--tracebacks",
        action="store_false",
        dest="log_rich_tracebacks",
        help="Enable rich tracebacks with syntax highlighting and formatting. Defaults to False."
    )
    group.addoption(
        "--tracebacks-width",
        metavar="num",
        action="store",
        type=int,
        dest="log_rich_tracebacks_width",
        default=None,
        help="Number of characters used to render tracebacks, or None for full width. Defaults to None.",
    )
    group.addoption(
        "--tracebacks-code-width",
        metavar="num",
        action="store",
        type=int,
        dest="log_rich_tracebacks_code_width",
        default=88,
        help="Number of code characters used to render tracebacks, or None for full width. Defaults to 88.",
    )
    group.addoption(
        "--tracebacks-extra-lines",
        metavar="num",
        action="store",
        type=int,
        dest="log_rich_tracebacks_extra_lines",
        default=None,
        help="Additional lines of code to render tracebacks, or None for full width. Defaults is 3.",
    )
    group.addoption(
        "--tracebacks-theme",
        type=str,
        default=None,
        help="Override pygments theme used in traceback.",
        dest="log_rich_tracebacks_theme",
    )
    group.addoption(
        "--tracebacks-word-wrap",
        action="store_true",
        dest="log_rich_tracebacks_word_wrap",
        help="Enable word wrapping of long tracebacks lines. Defaults to True."
    )
    group.addoption(
        "--tracebacks-show-locals",
        action="store_false",
        dest="log_rich_tracebacks_show_locals",
        help="Enable display of locals in tracebacks. Defaults to False."
    )
    parser.addini("tracebacks_suppress", type="args", help="Optional sequence of modules or paths to exclude from traceback.", default=())
    group.addoption(
        "--tracebacks-max-frames",
        metavar="num",
        action="store",
        type=int,
        dest="log_rich_tracebacks_max_frames",
        default=100,
        help="Optional maximum number of frames returned by traceback. Default to 100",
    )
    group.addoption(
        "--locals-max-length",
        metavar="num",
        action="store",
        type=int,
        dest="log_rich_locals_max_length",
        default=10,
        help="Maximum length of containers before abbreviating, Defaults to 10.",
    )
    group.addoption(
        "--locals-max-string",
        metavar="num",
        action="store",
        type=int,
        dest="log_rich_locals_max_string",
        default=80,
        help="Maximum length of string before truncating, Defaults to 80.",
    )
    group.addoption(
        "--keywords",
        action="append",
        default=None,
        metavar="LIST",
        help="List of words to highlight instead of ``RichHandler.KEYWORDS``.",
        dest="log_rich_keywords",
    )


@pytest.hookimpl(trylast=True)
def pytest_configure(config: pytest.Config) -> None:
    from _pytest.logging import get_option_ini
    from rich.logging import RichHandler

    setting_name = "log_rich_level"
    log_rich_level = get_log_level_for_setting(setting_name)
    enabled = config.getoption("--log-rich-level") is not None or config.getini("log_rich")
    if not enabled:
        return




    rich_format = get_option_ini(config, "--log-rich-format")
    datefmt = get_option_ini(config, "--log-rich-date-fmt")
    logging.basicConfig(
        level="NOTSET",
        format=rich_format,
        datefmt=datefmt,
        handlers=[handler],
    )
    log = logging.getLogger("conftest")
    log.info("Server starting...")
    logging.info("Server stopped...")

    config.pluginmanager.register("")


