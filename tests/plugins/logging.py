# Project : baloto-colombia
# File Name : logging.py
# Dir Path : tests/plugins
# Created on: 2025–06–05 at 23:00:43.

from __future__ import annotations

import logging
import sys
from argparse import Action
from enum import StrEnum
from typing import TYPE_CHECKING, Literal, Any, Sequence

import pytest

from baloto.cleo.io.outputs.output import Verbosity
from tests.helpers import add_option_ini
from baloto.core.config.settings import settings

if TYPE_CHECKING:
    IniLiteral = Literal["string", "paths", "pathlist", "args", "linelist", "bool"]
    from rich.highlighter import Highlighter
    from argparse import ArgumentParser, Namespace, ArgumentTypeError


__all__ = ("PLUGIN_NAME",)


PLUGIN_NAME = "baloto-logging"


class StoreHighlighter(Action):

    def __call__(
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        values: str | Sequence[Any] | None,
        option_string: str | None = None,
    ) -> None:
        setattr(namespace, self.dest, values)


@pytest.hookimpl
def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup(
        "logging", "Additional configuration for displaying rich-logging", after="tracebacks"
    )

    add_option_ini(
        parser,
        group,
        opts=["--logging-show-time", "--showtime"],
        dest="logging_show_time",
        action="store_false",
        default=True,
        ini_type="bool",
        help="Show a column for the time. Defaults to True.",
    )

    group.addoption(
        "--no-showtime",
        action="store_true",
        dest="logging_show_time",
        help="Hide column for the time. (negate --showtime passed through addopts)",
    )

    add_option_ini(
        parser,
        group,
        opts=["--logging-omit-repeated-times", "--omit-repeated"],
        dest="logging_omit_repeated_times",
        action="store_false",
        ini_type="bool",
        default=True,
        help="Omit repetition of the same time. Defaults to True.",
    )

    group.addoption(
        "--no-omit-repeated",
        action="store_true",
        dest="logging_omit_repeated_times",
        help="Repeats column for the time. (negate --omit-repeated passed through addopts)",
    )

    add_option_ini(
        parser,
        group,
        opts=["--logging-show-level", "--showlevel"],
        dest="logging_show_level",
        action="store_false",
        default=True,
        ini_type="bool",
        help="Show a column for the level. Defaults to True.",
    )
    group.addoption(
        "--no-showlevel",
        action="store_true",
        dest="logging_show_level",
        help="Removes the logging level. (negate --showlevel passed through addopts)",
    )

    add_option_ini(
        parser,
        group,
        opts=["--logging-show-path", "--show-path"],
        dest="logging_show_path",
        action="store_false",
        default=True,
        ini_type="bool",
        help="Show the path to the original log call. Defaults to True.",
    )

    group.addoption(
        "--no-showpath",
        action="store_true",
        dest="logging_show_path",
        help="Removes the logging path. (negate --show-path passed through addopts)",
    )

    add_option_ini(
        parser,
        group,
        opts=["--logging-enable-link-path", "--linkpath"],
        dest="logging_enable_link_path",
        action="store_false",
        default=True,
        ini_type="bool",
        help="Show the path to the original log call. Defaults to True.",
    )
    group.addoption(
        "--no-linkpath",
        action="store_true",
        dest="logging_enable_link_path",
        help="Removes links for the path. (negate --linkpath passed through addopts)",
    )

    parser.addini(
        "logging_markup",
        type="bool",
        default=settings.logging.markup,
        help="Enable console markup in log messages. Defaults to False.",
    )

    add_option_ini(
        parser,
        group,
        opts=["--logging-rich-tracebacks", "-R"],
        dest="logging_rich_tracebacks",
        action="store_false",
        default=True,
        ini_type="bool",
        help="Enable rich tracebacks with syntax highlighting and formatting. Defaults to False.",
    )

    group.addoption(
        "--logging-keywords",
        "--keywords",
        action="append",
        default=None,
        dest="logging_keywords",
        metavar="list",
        help="List of words to highlight instead of ``RichHandler.KEYWORDS``.",
    )


@pytest.hookimpl(trylast=True)
def pytest_configure(config: pytest.Config) -> None:
    from _pytest.logging import get_option_ini

    log_level = get_option_ini(config, "log_level")
    if log_level is None:
        log_level = settings.logging.level
    if isinstance(log_level, str):
        log_level = log_level_for_setting(config, "log_level")

    if not sys.stdin.isatty():
        settings.logging.enable_link_path = False

    from baloto.core.rich.logging.console_handler import ConsoleHandler

    settings.logging.markup = config.getini("logging_markup")
    handler_options = dict(
        show_time=settings.logging.show_time,
        omit_repeated_times=settings.logging.omit_repeated_times,
        show_level=settings.logging.show_level,
        show_path=settings.logging.show_path,
        enable_link_path=settings.logging.enable_link_path,
        highlighter=settings.console.highlighter,
        markup=settings.logging.markup,
        rich_tracebacks=settings.logging.rich_tracebacks,
        tracebacks_extra_lines=settings.tracebacks.extra_lines,
        tracebacks_theme=settings.console.theme,
        tracebacks_show_locals=settings.tracebacks.show_locals,
        tracebacks_max_frames=settings.tracebacks.max_frames,
        keywords=settings.logging.keywords,
    )

    try:
        from tests import get_console_key, create_console_key

        console_key = get_console_key()
        console = config.stash.get(console_key, None)
        if console is None:
            console = create_console_key(config)

        rich_handler = ConsoleHandler(log_level, console, **handler_options)
    except ValueError as e:
        if str(e).startswith("Unknown level"):
            raise pytest.UsageError(
                f"'{log_level}' is not recognized as a logging level name for "
                f"'log_level'. Please consider passing the logging level num instead."
            ) from e
        raise e from e

    def reset_logging() -> None:
        # -- Remove all handlers from the root logger
        root = logging.getLogger()
        for h in root.handlers[:]:
            root.removeHandler(h)
        # -- Reset logger hierarchy, this clears the internal dict of loggers
        logging.Logger.manager.loggerDict.clear()

    log_format = get_option_ini(config, "log_format")
    log_date_format = get_option_ini(config, "log_date_format")

    config.add_cleanup(reset_logging)
    reset_logging()
    logging.basicConfig(
        level=logging.NOTSET,
        format=log_format,
        datefmt=log_date_format,
        handlers=[rich_handler],
    )
    logging.captureWarnings(True)


def pytest_unconfigure(config: pytest.Config) -> None:
    from tests import get_console_key

    console_key = get_console_key()
    console = config.stash.get(console_key, None)
    if console:
        del console
        config.stash.__delitem__(console_key)


def log_level_for_setting(config: pytest.Config, setting_name: str) -> int | str:
    log_level: int | str = config.getoption(setting_name)
    if log_level is None:
        log_level = config.getini(setting_name)
    if log_level is None:
        return logging.NOTSET
    if isinstance(log_level, str):
        return log_level.upper()
    return log_level
