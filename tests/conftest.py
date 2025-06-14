"""
PYTEST_DONT_REWRITE
"""

# https://github.com/TvoroG/pytest-lazy-fixture
# https://random-words-api.kushcreates.com/

# import json
# from urllib.request import urlopen
# users = json.loads(urlopen("https://randomuser.me/api/?results=30").read())["results"]

from __future__ import annotations

import os
import sys
from io import StringIO
from typing import TYPE_CHECKING

import pytest

from baloto.cleo.io.inputs.string_input import StringInput
from baloto.cleo.io.outputs.output import Verbosity
from baloto.core.config.settings import settings

if TYPE_CHECKING:
    from baloto.cleo.io.buffered_io import BufferedIO
    from baloto.cleo.io.stream_io import StreamIO
    from baloto.cleo.io.null_io import NullIO

pytest_plugins = ("tests.plugins.logging",)


@pytest.hookimpl
def pytest_addoption(parser: pytest.Parser, pluginmanager: pytest.PytestPluginManager) -> None:

    group = parser.getgroup("baloto", description="main application testing configuration")
    group.addoption(
        "--stream", "-S",
        action="store_true",
        dest="stream",
        help="Enable streaming rich console outputs to stdout inside tests",
    )
    parser.addini("unregister_plugins", type="linelist", help="lits of plugin names to be unregister the plugins as soon as they were registeres")


@pytest.hookimpl(tryfirst=True)
def pytest_cmdline_main(config: pytest.Config) -> pytest.ExitCode | int | None:
    if not "--strict-markers" in config.invocation_params.args:
        config.known_args_namespace.strict_markers = True
        config.option.strict_markers = True
    if not "--strict-config" in config.invocation_params.args:
        config.known_args_namespace.strict_config = True
        config.option.strict_config = True
    config.known_args_namespace.keepduplicates = False

    force_normal = int(os.getenv("FORCE_VERBOSITY_NORMAL", 0))
    if force_normal:
        settings.verbosity = Verbosity.NORMAL
        return


    if settings.debugger_mode:
        settings.verbosity = Verbosity.DEBUG
        config.option.maxfail = 1
        config.known_args_namespace.showlocals = True  # ?
        config.option.shwofixtures = True
        config.option.reportchars = "fExXs"
        config.option.log_level = "DEBUG"
        config.known_args_namespace.trace_config = True  # ?
        config.known_args_namespace.no_header = False
        config.known_args_namespace.no_summary = False

    return None


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config: pytest.Config) -> None:

    config.option.verbose = int(settings.verbosity.value)
    settings.tracebacks.show_locals = config.option.showlocals

    if sys.stdout.isatty():
        settings.console.legacy_windows = None
    else:
        settings.console.legacy_windows = False
        settings.console.environ = {"COLUMNS": "190", "LINES": "25"}

    if settings.verbosity == Verbosity.QUIET:
        settings.console.quiet = True

    if settings.verbosity == Verbosity.NORMAL:
        show_locals = config.option.showlocals
        settings.tracebacks.show_locals = show_locals
        settings.tracebacks.max_frames = 5

    if settings.verbosity > Verbosity.NORMAL:
        settings.tracebacks.max_frames = 10

    if settings.verbosity > Verbosity.VERBOSE:
        settings.tracebacks.max_frames = 50

    if settings.verbosity > Verbosity.VERY_VERBOSE:
        settings.tracebacks.max_frames = 100

    from tests.plugins import tracker
    config.pluginmanager.register(tracker, tracker.PLUGIN_NAME)

    from baloto.core.tester import rich_testers
    plugin = rich_testers.rich_plugin_manager().get_plugin("rich-logging")
    if plugin:
        config.add_cleanup(rich_testers.cleanup_factory(plugin))


@pytest.hookimpl
def pytest_unconfigure(config: pytest.Config) -> None:
    from tests.plugins import tracker
    if config.pluginmanager.has_plugin(tracker.PLUGIN_NAME):
        plugin = config.pluginmanager.get_plugin(tracker.PLUGIN_NAME)
        config.pluginmanager.unregister(plugin, tracker.PLUGIN_NAME)


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





# def pytest_collection_modifyitems(
#     session: pytest.Session, config: pytest.Config, items: list[pytest.Item]
# ) -> None:
#     selected, deselected_by_testcase = select_by_testcase(items, config)
#     selected, deselected_by_labels = select_by_labels(selected, config)
#
#     items[:] = selected
#
#     if deselected_by_testcase or deselected_by_labels:
#         config.hook.pytest_deselected(items=[*deselected_by_testcase, *deselected_by_labels])
