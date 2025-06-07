# Project : baloto-colombia
# File Name : logging.py
# Dir Path : tests/plugins
# Created on: 2025–06–05 at 23:00:43.

from __future__ import annotations

import logging
from argparse import Action
from typing import TYPE_CHECKING, Literal, Any, Sequence

import pytest

from baloto.cleo.io.outputs.console_output import ConsoleOutput
from baloto.cleo.io.outputs.output import Verbosity

if TYPE_CHECKING:
    IniLiteral = Literal['string', 'paths', 'pathlist', 'args', 'linelist', 'bool']
    from rich.highlighter import Highlighter
    from argparse import ArgumentParser, Namespace, ArgumentTypeError


__all__ = ("PLUGIN_NAME", )


PLUGIN_NAME = "miloto-logging"


class StoreHighlighter(Action):

    def __call__(
        self, parser: ArgumentParser, namespace: Namespace, values: str | Sequence[Any] | None, option_string: str | None = None
    ) -> None:
        setattr(namespace, self.dest, values)


@pytest.hookimpl
def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("logging", "Additional configuration for displaying rich-logging", after="miloto")

    def add_option_ini(option: str, dest: str, default: Any = None, type: IniLiteral | None = None, **kwargs: Sequence[str]) -> None:
        parser.addini(
            dest, default=default, type=type, help="Default value for " + option
        )
        group.addoption(option, dest=dest, **kwargs)

    add_option_ini(
        "--show-time",
        dest="logging_show_time",
        action="store_false",
        default=True,
        type="bool",
        help="Show a column for the time. Defaults to True."
    )

    add_option_ini(
        "--omit-repeated-times",
        dest="logging_omit_repeated_times",
        action="store_false",
        default=True,
        type="bool",
        help="Omit repetition of the same time. Defaults to True."
    )

    add_option_ini(
        "--show-level",
        dest="logging_show_level",
        action="store_false",
        default=True,
        type="bool",
        help="Show a column for the level. Defaults to True."
    )
    add_option_ini(
        "--show-path",
        dest="logging_show_path",
        action="store_false",
        default=True,
        type="bool",
        help="Show the path to the original log call. Defaults to True."
    )

    add_option_ini(
        "--enable-link-path",
        dest="logging_enable_link_path",
        action="store_false",
        default=True,
        type="bool",
        help="Show the path to the original log call. Defaults to True."
    )
    group.addoption(
        '--highlighter',
        action=StoreHighlighter,
        default=None,
        dest="logging_highlighter",
        metavar='TYPE',
        type=validate_highlighter,
        help='Highlighter to style log messages, Defaults to use ReprHighlighter.',
    )

    group.addoption(
        "--markup",
        action="store_true",
        dest="logging_rich_markup",
        help="Enable console markup in log messages. Defaults to False."
    )
    group.addoption(
        "--rich-tracebacks",
        action="store_true",
        dest="logging_rich_tracebacks",
        help="Enable rich tracebacks with syntax highlighting and formatting. Defaults to %(default)s."
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
    from baloto.cleo.rich.logging.console_handler import ConsoleHandler
    from _pytest.logging import get_option_ini

    log_level = log_level_for_setting(config, "log_level")
    log_format = get_option_ini(config, "log_format")
    log_date_format = get_option_ini(config, "log_date_format")

    handler_options = dict(
        show_time=get_option_ini(config, "logging_show_time"),
        omit_repeated_times=get_option_ini(config, "logging_omit_repeated_times"),
        show_level=get_option_ini(config, "logging_show_level"),
        show_path=get_option_ini(config, "logging_show_path"),
        enable_link_path=get_option_ini(config, "logging_enable_link_path"),
        highlighter=config.getoption("--highlighter"),
        markup=config.getoption("--markup"),
        rich_tracebacks=config.getoption("--rich-tracebacks"),
        tracebacks_width=config.getoption("--tracebacks-width"),
        tracebacks_code_width=config.getoption("--tracebacks-code-width"),
        tracebacks_extra_lines=config.getoption("--tracebacks-extra-lines"),
        tracebacks_theme=config.getoption("--tracebacks-theme"),
        tracebacks_word_wrap=config.getoption("--tracebacks-word-wrap"),
        tracebacks_show_locals=config.getoption("--tracebacks-show-locals"),
        tracebacks_suppress=config.getini("tracebacks_suppress"),
        tracebacks_max_frames=config.getoption("--tracebacks-max-frames"),
        locals_max_length=config.getoption("--locals-max-length"),
        locals_max_string=config.getoption("--locals-max-string"),
        keywords=config.getoption("--keywords")
    )

    try:
        from tests import get_console_output_key
        console_output_key = get_console_output_key()
        console_output = config.stash.get(console_output_key, None)
        if console_output is None:
            console_output = ConsoleOutput.stdout_console(verbosity=config.option.verbose)
            config.stash.setdefault(console_output_key, console_output)

        rich_handler = ConsoleHandler(log_level, getattr(console_output, "_console"), **handler_options)
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