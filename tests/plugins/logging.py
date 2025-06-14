# Project : baloto-colombia
# File Name : logging.py
# Dir Path : tests/plugins
# Created on: 2025–06–05 at 23:00:43.

from __future__ import annotations

import logging
import sys
from argparse import Action
from typing import Any
from typing import Literal
from typing import Sequence
from typing import TYPE_CHECKING

import pytest

from baloto.core.config.settings import settings
from tests.helpers import add_option_ini

if TYPE_CHECKING:
    IniLiteral = Literal["string", "paths", "pathlist", "args", "linelist", "bool"]
    from argparse import ArgumentParser, Namespace

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
    import tomllib
    from baloto.core.tester.rich_testers import rich_plugin_manager
    with open(config.inipath, "rb") as poetry_file:
        data = tomllib.load(poetry_file)

    rich_plugin_manager().hook.rich_configure.call_historic(kwargs=dict(config=config, poetry=data))

