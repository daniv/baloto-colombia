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
from helpers import add_option_ini

if TYPE_CHECKING:
    IniLiteral = Literal["string", "paths", "pathlist", "args", "linelist", "bool"]
    from rich.highlighter import Highlighter
    from argparse import ArgumentParser, Namespace, ArgumentTypeError


__all__ = ("PLUGIN_NAME", "LoggingOptions")


PLUGIN_NAME = "miloto-logging"


class LoggingOptions(StrEnum):
    ENABLE_LINK_PATH = "logging_enable_link_path"
    SHOW_PATH = "logging_show_path"
    HIGHLIGHTER = "logging_highlighter"
    SHOW_LEVEL = "logging_show_level"
    OMIT_REPEATED_TIMES = "logging_omit_repeated_times"
    SHOW_TIME = "logging_show_time"
    MARKUP = "logging_markup"
    RICH_TRACEBACKS = "logging_rich_tracebacks"
    KEYWORDS = "logging_keywords"


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
        "logging", "Additional configuration for displaying rich-logging", after="miloto"
    )

    add_option_ini(
        parser,
        group,
        opts=["--logging-show-time", "--showtime"],
        dest=LoggingOptions.SHOW_TIME,
        action="store_false",
        default=True,
        ini_type="bool",
        help="Show a column for the time. Defaults to True.",
    )

    group.addoption(
        "--no-showtime",
        action="store_true",
        dest=LoggingOptions.SHOW_PATH,
        help="Hide column for the time. (negate --showtime passed through addopts)",
    )

    add_option_ini(
        parser,
        group,
        opts=["--logging-omit-repeated-times", "--omit-repeated"],
        dest=LoggingOptions.OMIT_REPEATED_TIMES,
        action="store_false",
        ini_type="bool",
        default=True,
        help="Omit repetition of the same time. Defaults to True.",
    )

    group.addoption(
        "--no-omit-repeated",
        action="store_true",
        dest=LoggingOptions.OMIT_REPEATED_TIMES,
        help="Repeats column for the time. (negate --omit-repeated passed through addopts)",
    )

    add_option_ini(
        parser,
        group,
        opts=["--logging-show-level", "--showlevel"],
        dest=LoggingOptions.SHOW_LEVEL,
        action="store_false",
        default=True,
        ini_type="bool",
        help="Show a column for the level. Defaults to True.",
    )
    group.addoption(
        "--no-showlevel",
        action="store_true",
        dest=LoggingOptions.SHOW_LEVEL,
        help="Removes the logging level. (negate --showlevel passed through addopts)",
    )

    add_option_ini(
        parser,
        group,
        opts=["--logging-show-path", "--show-path"],
        dest=LoggingOptions.SHOW_PATH,
        action="store_false",
        default=True,
        ini_type="bool",
        help="Show the path to the original log call. Defaults to True.",
    )

    group.addoption(
        "--no-showpath",
        action="store_true",
        dest=LoggingOptions.SHOW_PATH,
        help="Removes the logging path. (negate --show-path passed through addopts)",
    )

    add_option_ini(
        parser,
        group,
        opts=["--logging-enable-link-path", "--linkpath"],
        dest=LoggingOptions.ENABLE_LINK_PATH,
        action="store_false",
        default=True,
        ini_type="bool",
        help="Show the path to the original log call. Defaults to True.",
    )
    group.addoption(
        "--no-linkpath",
        action="store_true",
        dest=LoggingOptions.ENABLE_LINK_PATH,
        help="Removes links for the path. (negate --linkpath passed through addopts)",
    )
    group.addoption(
        "--logging-highlighter",
        action=StoreHighlighter,
        default=None,
        dest=LoggingOptions.HIGHLIGHTER,
        metavar="TYPE",
        type=validate_highlighter,
        help="Highlighter to style log messages, Defaults to use ReprHighlighter.",
    )

    group.addoption(
        "--logging-markup",
        "--markup",
        action="store_true",
        dest=LoggingOptions.MARKUP,
        help="Enable console markup in log messages. Defaults to False.",
    )
    group.addoption(
        "--no-markup",
        action="store_false",
        dest=LoggingOptions.MARKUP,
        help="Disable markup on logging messages. (negate --markup passed through addopts)",
    )
    add_option_ini(
        parser,
        group,
        opts=["--logging-rich-tracebacks", "-R"],
        dest=LoggingOptions.RICH_TRACEBACKS,
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
        dest=LoggingOptions.KEYWORDS,
        metavar="list",
        help="List of words to highlight instead of ``RichHandler.KEYWORDS``.",
    )


def pytest_unconfigure(config: pytest.Config) -> None:
    from tests import get_console_key

    console_key = get_console_key()
    console = config.stash.get(console_key, None)
    if console:
        del console
        config.stash.__delitem__(console_key)


@pytest.hookimpl(trylast=True)
def pytest_configure(config: pytest.Config) -> None:
    from baloto.cleo.rich.logger.console_handler import ConsoleHandler
    from _pytest.logging import get_option_ini

    log_level = log_level_for_setting(config, "log_level")
    log_format = get_option_ini(config, "log_format")
    log_date_format = get_option_ini(config, "log_date_format")

    if not sys.stdin.isatty():
        config.option.logging_enable_link_path = False

    max_frames = 50
    if config.option.verbose == Verbosity.NORMAL:
        max_frames = 2
    elif config.option.verbose == Verbosity.DEBUG:
        max_frames = None

    handler_options = dict(
        show_time=get_option_ini(config, "logging_show_time"),
        omit_repeated_times=get_option_ini(config, "logging_omit_repeated_times"),
        show_level=get_option_ini(config, "logging_show_level"),
        show_path=get_option_ini(config, "logging_show_path"),
        enable_link_path=get_option_ini(config, "logging_enable_link_path"),
        highlighter=config.getoption("--logging-highlighter"),
        markup=config.getoption("--logging-markup"),
        rich_tracebacks=config.getoption("logging_rich_tracebacks"),
        tracebacks_extra_lines=config.getini("tracebacks_extra_lines"),
        tracebacks_theme=config.getoption("--tracebacks-theme"),
        tracebacks_show_locals=config.getoption("--tracebacks-show-locals"),
        tracebacks_max_frames=max_frames,
        keywords=config.getoption("--logging-keywords"),
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

    config.add_cleanup(reset_logging)
    reset_logging()
    logging.basicConfig(
        level=logging.NOTSET,
        format=log_format,
        datefmt=log_date_format,
        handlers=[rich_handler],
    )
    logging.captureWarnings(True)


def validate_highlighter(arg: str | None) -> Highlighter | None:
    if arg is None:
        return None
    try:
        code = (
            f"import rich; "
            f"instance = {arg}(); "
            f"assert isinstance(instance, rich.highlighter.Highlighter)"
        )
        compile(code, "<string>", "exec")
        exec(code, locals())
    except (NameError, Exception, AssertionError) as e:
        raise ArgumentTypeError(f"invalid highlighter -> {str(e)}") from e

    return locals().get("instance")


def log_level_for_setting(config: pytest.Config, setting_name: str) -> int | str:
    log_level: int | str = config.getoption(setting_name)
    if log_level is None:
        log_level = config.getini(setting_name)
    if log_level is None:
        return logging.NOTSET
    if isinstance(log_level, str):
        return log_level.upper()
    return log_level
