import logging
import sys
import textwrap
from pathlib import Path
from typing import ClassVar

import pytest
from _pytest import annotations
import allure_commons

from tests import AllureStepLogger


def pytest_addoption(parser: pytest.Parser):
    """Add a cmdline option --allure-step-log-level."""
    parser.getgroup("logging").addoption(
        "--allure-step-log-level",
        dest="allure_step_log_level",
        default="debug",
        metavar="ALLURE_STEP_LEVEL",
        help="Level of allure.step log messages. 'DEBUG' by default."
    )

from rich.console import Console

from abc import ABC
from abc import abstractmethod
import re
from rich.style import Style


class Formatter(ABC):
    @abstractmethod
    def format(self, msg: str) -> str: ...

class BuilderLogFormatter(Formatter):
    def format(self, msg: str) -> str:
        if msg.startswith("Building "):
            msg = re.sub("Building (.+)", "  - Building <info>\\1</info>", msg)
        elif msg.startswith("Built "):
            msg = re.sub("Built (.+)", "  - Built <success>\\1</success>", msg)
        elif msg.startswith("Adding: "):
            msg = re.sub("Adding: (.+)", "  - Adding: <b>\\1</b>", msg)
        elif msg.startswith("Executing build script: "):
            msg = re.sub(
                "Executing build script: (.+)",
                "  - Executing build script: <b>\\1</b>",
                msg,
            )

        return msg

FORMATTERS = {
    "poetry.core.masonry.builders.builder": BuilderLogFormatter(),
    "poetry.core.masonry.builders.sdist": BuilderLogFormatter(),
    "poetry.core.masonry.builders.wheel": BuilderLogFormatter(),
}

POETRY_FILTER = logging.Filter(name="poetry")
class IOFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        if not record.exc_info:
            level = record.levelname.lower()
            msg = record.msg

            if record.name in FORMATTERS:
                msg = FORMATTERS[record.name].format(msg)
            # elif level in self._colors:
            else:
                msg = f"[{level}]{msg}[/]"

            record.msg = msg

        formatted = super().format(record)

        if not POETRY_FILTER.filter(record):
            # prefix all lines from third-party packages for easier debugging
            formatted = textwrap.indent(
                formatted, f"[{_log_prefix(record)}] ", lambda line: True
            )

        return formatted


class ConsoleHandler(logging.Handler):
    def __init__(self, console: Console) -> None:
        self._console = console

        super().__init__()

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            level = record.levelname.lower()
            err = level in ("warning", "error", "exception", "critical")
            if err:
                self._io.write_error_line(msg)
            else:
                self._console.print(msg)
                self._console.print(f"\[mama.papap\] {msg}", highlight=True)
        except Exception:
            self.handleError(record)

from rich.theme import Theme

miloto_theme = Theme(
        {
            "error": Style(color="red", bold=True),
            "warning": Style(color="dark_goldenrod", bold=True),
            "info": Style(color="blue", bold=False),
            "debug": Style(bold=False, dim=True),


            "switch": Style(color="green", bold=True),
            "option": Style(color="bright_cyan", bold=True),
            "debug.option": Style(color="bright_cyan", bold=True, italic=True),
            "debug.argument": Style(color="bright_magenta", bold=True, italic=True),
            "argument": Style(color="bright_magenta", bold=True),
            "command": Style(color="magenta", bold=True),
            "prog": Style(color="medium_orchid3", bold=True),
            "metavar": Style(color="yellow", bold=True),
            "money": Style(color="green3", bold=True),
            "report": Style(bold=True, italic=True),
            "date": Style(color="green", italic=True),

            "help.var": Style(color="gray58", italic=True),
            "cmd.class": Style(italic=True, color="bright_cyan"),
            "cmd.def": Style(italic=True, color="bright_cyan"),
            "cmd.callable": Style(italic=True, color="bright_cyan"),
            "cmd.var": Style(italic=True, color="bright_cyan"),
            "debug.hex": Style(italic=True, color="green_yellow"),
        }
    )

@pytest.hookimpl
def pytest_configure(config: pytest.Config):
    import sys
    console = Console(theme=miloto_theme, log_time=False, file=sys.stdout, force_interactive=True)
    handler = ConsoleHandler(console)
    handler.setFormatter(IOFormatter())

    # log_format = '%(asctime)s  %(user)-8s %(message)s'
    logging.basicConfig(level=logging.DEBUG, handlers=[handler])
    # handler.addFilter(POETRY_FILTER)
    logger = logging.getLogger(__name__)
    logger.info("eiririirir")


    """Register `allure_step_logger` plugin if `allure_pytest` plugin is registered."""
    if config.pluginmanager.getplugin('allure_pytest'):
        allure_commons.plugin_manager.register(AllureStepLogger(config), "allure_step_logger")



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



def _log_prefix(record: logging.LogRecord) -> str:
    prefix = _path_to_package(Path(record.pathname)) or record.module
    if record.name != "root":
        prefix = ":".join([prefix, record.name])
    return prefix


def _path_to_package(path: Path) -> str | None:
    """Return main package name from the LogRecord.pathname."""
    prefix: Path | None = None
    # Find the most specific prefix in sys.path.
    # We have to search the entire sys.path because a subsequent path might be
    # a sub path of the first match and thereby a better match.
    for syspath in sys.path:
        if (
            prefix and prefix in (p := Path(syspath)).parents and p in path.parents
        ) or (not prefix and (p := Path(syspath)) in path.parents):
            prefix = p
    if not prefix:
        # this is unexpected, but let's play it safe
        return None
    path = path.relative_to(prefix)
    return path.parts[0]  # main package name