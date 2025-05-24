from __future__ import annotations

import logging
import sys
import textwrap
from pathlib import Path
from typing import ClassVar, TYPE_CHECKING

import pytest

# from tests import AllureStepLogger

from rich.console import Console

from abc import ABC
from abc import abstractmethod
import re
from rich.style import Style
from rich.console import Console
from rich.theme import Theme
from baloto.core.cleo.formatters.formatter import Formatter
from baloto.core.cleo.io.outputs.console_output import ConsoleOutput
from baloto.core.cleo.io.io import IO
from rich.theme import Theme

# miloto_theme = Theme(
#     {
#         "error": Style(color="red", bold=True),
#         "warning": Style(color="dark_goldenrod", bold=True),
#         "info": Style(color="blue", bold=False),
#         "debug": Style(bold=False, dim=True),
#         "switch": Style(color="green", bold=True),
#         "option": Style(color="bright_cyan", bold=True),
#         "debug.option": Style(color="bright_cyan", bold=True, italic=True),
#         "debug.argument": Style(color="bright_magenta", bold=True, italic=True),
#         "argument": Style(color="bright_magenta", bold=True),
#         "command": Style(color="magenta", bold=True),
#         "prog": Style(color="medium_orchid3", bold=True),
#         "metavar": Style(color="yellow", bold=True),
#         "money": Style(color="green3", bold=True),
#         "report": Style(bold=True, italic=True),
#         "date": Style(color="green", italic=True),
#         "help.var": Style(color="gray58", italic=True),
#         "cmd.class": Style(italic=True, color="bright_cyan"),
#         "cmd.def": Style(italic=True, color="bright_cyan"),
#         "cmd.callable": Style(italic=True, color="bright_cyan"),
#         "cmd.var": Style(italic=True, color="bright_cyan"),
#         "debug.hex": Style(italic=True, color="green_yellow"),
#     }
# )

# @pytest.hookimpl
# def pytest_configure(config: pytest.Config):
#     import sys
#     console = Console(theme=miloto_theme, file=sys.stdout, force_interactive=True)
#     error_console = Console(theme=miloto_theme, stderr=True)
#     handler = ConsoleHandler(console, error_console)
#     handler.setFormatter(IOFormatter())
#
#     # log_format = '%(asctime)s %(message)s'
#     logging.basicConfig(level=logging.DEBUG, handlers=[handler])
#     # handler.addFilter(POETRY_FILTER)
#     logger = logging.getLogger(__name__)
#     logger.info("eiririirir")
#
#
#     """Register `allure_step_logger` plugin if `allure_pytest` plugin is registered."""
#     if config.pluginmanager.getplugin('allure_pytest'):
#         allure_commons.plugin_manager.register(AllureStepLogger(config), "allure_step_logger")


@pytest.hookimpl(tryfirst=True)
def pytest_cmdline_main(config: pytest.Config) -> pytest.ExitCode | int | None:
    from _pytest.outcomes import Skipped

    # from itertools import product
    # combinations8 = list(product(range(2), repeat=8))
    # combinations8 = list(filter(lambda x: sum(x) == 5, combinations8))
    # combinations10 = list(product(range(2), repeat=10))
    # combinations10 = list(filter(lambda x: sum(x) == 5, combinations10))

    if not "--strict-markers" in config.invocation_params.args:
        config.option.strict_markers = True
    if not "--strict-config" in config.invocation_params.args:
        config.option.strict_config = True

    config.option.ignore_glob = ["*__init*", "*.log"]
    return None


FORMATTER = Formatter({"switch": Style(color="green", italic=True)})


@pytest.fixture(scope="session", name="theme")
def create_theme() -> Theme:
    return FORMATTER.create_theme()


@pytest.fixture(scope="session", name="console")
def create_console(theme) -> Console:
    return Console(theme=theme, file=sys.stdout, force_interactive=True)


@pytest.fixture(scope="session", name="error_console")
def create_error_console(theme) -> Console:
    return Console(theme=theme, stderr=True, style="error", force_interactive=False)


@pytest.fixture(scope="session", name="error_console_output")
def create_error_console_output(error_console: Console, theme: Theme) -> ConsoleOutput:
    from baloto.core.cleo.io.outputs.console_output import ConsoleOutput

    return ConsoleOutput(error_console)


@pytest.fixture(scope="session", name="console_output")
def create_console_output(console: Console) -> ConsoleOutput:
    from baloto.core.cleo.io.outputs.console_output import ConsoleOutput

    return ConsoleOutput(console)


@pytest.fixture(scope="session", name="baloto_io")
def create_io(console_output: ConsoleOutput, error_console_output: ConsoleOutput) -> IO:
    from baloto.core.cleo.io.inputs.argv_input import ArgvInput

    input = ArgvInput()
    input.stream = sys.stdin
    return IO(input, console_output, error_console_output)
