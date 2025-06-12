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
from typing import TYPE_CHECKING

import pytest

from baloto.cleo.io.outputs.output import Verbosity
from tests.helpers import cleanup_factory
from baloto.core.config.settings import settings

if TYPE_CHECKING:
    pass


# pytest_plugins = ("plugins.bootstrap",)
DISABLE_PRINT = bool(int(os.getenv("DISABLE_PRINT", False)))
DISABLE_MSG = "run unit-test no requires printing env.DISABLE_PRINT set to True"
# MILOTO_LABEL_MARK = "miloto_label"


@pytest.hookimpl
def pytest_addoption(parser: pytest.Parser, pluginmanager: pytest.PytestPluginManager) -> None:

    group = parser.getgroup("baloto", description="main application testing configuration")
    # group.addoption(
    #     "--rich-tracebacks",
    #     action="store_true",
    #     dest="logging_rich_tracebacks",
    #     help="Enable rich tracebacks with syntax highlighting and formatting. Defaults to %(default)s."
    # )

    # group.addoption('--miloto-features',
    #                                      action="store",
    #                                      dest="allure_features",
    #                                      metavar="FEATURES_SET",
    #                                      default={},
    #                                      type=label_type(LabelType.FEATURE),
    #                                      help="""Comma-separated list of feature names.
    #                                       Run tests that have at least one of the specified feature labels.""")

    #
    # test_mode = os.getenv("TESTMODE", 'False').lower() in ('true', '1', 't')
    # if test_mode:
    #     from tests.plugins import testmode_plugin
    #     pluginmanager.register(testmode_plugin, testmode_plugin.PLUGIN_NAME)


@pytest.hookimpl(tryfirst=True)
def pytest_cmdline_main(config: pytest.Config) -> pytest.ExitCode | int | None:
    if not "--strict-markers" in config.invocation_params.args:
        config.known_args_namespace.strict_markers = True
        config.option.strict_markers = True
    if not "--strict-config" in config.invocation_params.args:
        config.known_args_namespace.strict_config = True
        config.option.strict_config = True
    config.known_args_namespace.keepduplicates = False

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
    config.add_cleanup(cleanup_factory(config, tracker))

    from tests.plugins import logging

    config.pluginmanager.register(logging, logging.PLUGIN_NAME)
    config.add_cleanup(cleanup_factory(config, logging))

    # config.addinivalue_line("markers", f"{MILOTO_LABEL_MARK}: miloto label marker")


@pytest.hookimpl
def pytest_unconfigure(config: pytest.Config) -> None: ...


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
