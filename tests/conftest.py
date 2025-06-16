"""
PYTEST_DONT_REWRITE
"""

# https://github.com/TvoroG/pytest-lazy-fixture
# https://random-words-api.kushcreates.com/

# import json
# from urllib.request import urlopen
# users = json.loads(urlopen("https://randomuser.me/api/?results=30").read())["results"]

from __future__ import annotations

import logging
import os
import sys
from io import StringIO
from typing import TYPE_CHECKING

import pytest
from pendulum import local
from rich import get_console

from baloto.cleo.io.inputs.string_input import StringInput
from baloto.cleo.io.outputs.output import Verbosity

if TYPE_CHECKING:
    from baloto.cleo.io.buffered_io import BufferedIO
    from baloto.cleo.io.stream_io import StreamIO
    from baloto.cleo.io.null_io import NullIO

pytest_plugins = ("tests.plugins.logging",)
collect_ignore = [
    "tests/miloto_tests",
    "tests/cleo_tests",
    "tests/rich_tests",
    "tests/difflib_diff.py",
    "tests/helpers",
]
collect_ignore_glob = [
    "**/ignore_me.py",    # Ignores files named ignore_me.py
    "tests/plugins/*",    # Ignores all files under the tests/plugins directory
    "*_temp.py"           # Ignores all files ending with _temp.py
]

@pytest.hookimpl
def pytest_addhooks(pluginmanager: pytest.PytestPluginManager) -> None:
    from tests.plugins.pytest_richtrace import hookspecs

    pluginmanager.add_hookspecs(hookspecs)


@pytest.hookimpl
def pytest_addoption(parser: pytest.Parser, pluginmanager: pytest.PytestPluginManager) -> None:

    group = parser.getgroup("baloto", description="main application testing configuration")
    group.addoption(
        "--stream",
        "-S",
        action="store_true",
        dest="stream",
        help="Enable streaming rich console outputs to stdout inside tests",
    )
    group.addoption(
        "--show-packages-versions",
        "--versions",
        action="store_true",
        dest="show_packages",
        help="displays detailed information the top-level and outdated packages available. see: poetry show -l -T",
    )


@pytest.hookimpl(tryfirst=True)
def pytest_cmdline_main(config: pytest.Config) -> pytest.ExitCode | int | None:
    if not "--strict-markers" in config.invocation_params.args:
        config.known_args_namespace.strict_markers = True
        config.option.strict_markers = True
    if not "--strict-config" in config.invocation_params.args:
        config.known_args_namespace.strict_config = True
        config.option.strict_config = True
    config.known_args_namespace.keepduplicates = False

    from baloto.core.richer import get_rich_settings

    rich_settings = get_rich_settings()
    # force_normal = int(os.getenv("FORCE_VERBOSITY_NORMAL", 0))
    # if force_normal:
    #     settings.verbosity = Verbosity.NORMAL
    #     return
    #
    #
    if rich_settings.debugging_mode:
        rich_settings.verbosity = Verbosity.DEBUG
        config.known_args_namespace.verbose = Verbosity.DEBUG.value
    #     config.option.maxfail = 1
    #     config.known_args_namespace.showlocals = True  # ?
    #     config.option.shwofixtures = True
    #     config.option.reportchars = "fExXs"
    #     config.option.log_level = "DEBUG"
    #     config.known_args_namespace.trace_config = True  # ?
    #     config.known_args_namespace.no_header = False
    #     config.known_args_namespace.no_summary = False
    #
    return None


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config: pytest.Config) -> None:

    from baloto.core.richer import get_rich_settings

    rich_settings = get_rich_settings()

    config.option.verbose = rich_settings.verbosity
    rich_settings.tracebacks.show_locals = config.option.showlocals

    if sys.stdout.isatty():
        rich_settings.console_settings.legacy_windows = None
    else:
        rich_settings.console_settings.legacy_windows = False
        rich_settings.console_settings.environ = {"COLUMNS": "190", "LINES": "25"}

    if rich_settings.verbosity == Verbosity.QUIET:
        rich_settings.console_settings.quiet = True

    if rich_settings.verbosity == Verbosity.NORMAL:
        show_locals = config.option.showlocals
        rich_settings.tracebacks.show_locals = show_locals
        rich_settings.tracebacks.max_frames = 5

    if rich_settings.verbosity > Verbosity.NORMAL:
        rich_settings.tracebacks.max_frames = 10

    if rich_settings.verbosity > Verbosity.VERBOSE:
        rich_settings.tracebacks.max_frames = 20

    if rich_settings.verbosity > Verbosity.VERY_VERBOSE:
        rich_settings.tracebacks.max_frames = 100

    from baloto.core.richer import setup_logging

    setup_logging()

    from tests.plugins.pytest_richtrace import plugin

    config.pluginmanager.register(plugin, plugin.PLUGIN_NAME)


@pytest.hookimpl
def pytest_unconfigure(config: pytest.Config) -> None:
    logger = logging.getLogger()
    for handler in logger.handlers:
        handler.close()
        logger.removeHandler(handler)

    from tests.plugins.pytest_richtrace import plugin

    if config.pluginmanager.has_plugin(plugin.PLUGIN_NAME):
        plugin = config.pluginmanager.get_plugin(plugin.PLUGIN_NAME)
        config.pluginmanager.unregister(plugin, plugin.PLUGIN_NAME)


@pytest.fixture(scope="session", autouse=True)
def stream(pytestconfig: pytest.Config) -> None:
    if not pytestconfig.option.stream:
        os.environ["STREAM"] = "False"


@pytest.fixture(scope="session")
def buffered_io() -> BufferedIO:
    from baloto.cleo.io.buffered_io import BufferedIO

    input_ = StringInput("")
    input_.stream = StringIO()
    return BufferedIO(input_)


@pytest.fixture(scope="session")
def stream_io(pytestconfig: pytest.Config) -> StreamIO | None:
    if pytestconfig.option.stream:
        from baloto.cleo.io.stream_io import StreamIO

        return StreamIO()
    return None


@pytest.fixture(scope="session")
def null_io() -> NullIO:
    from baloto.cleo.io.null_io import NullIO

    return NullIO()
