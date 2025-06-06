"""
PYTEST_DONT_REWRITE
"""

# https://github.com/TvoroG/pytest-lazy-fixture

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, Any, Callable, Literal, Sequence

import pytest

from rich.console import Console

from helpers import cleanup_factory

if TYPE_CHECKING:
    pass


DISABLE_PRINT = bool(int(os.getenv("DISABLE_PRINT", False)))
DISABLE_MSG = "run unit-test no requires printing env.DISABLE_PRINT was set to True"
MILOTO_LABEL_MARK = 'miloto_label'

@pytest.hookimpl
def pytest_addoption(parser: pytest.Parser, pluginmanager: pytest.PytestPluginManager) -> None:
    from tests.plugins import tracebacks
    from tests.plugins import logging

    pluginmanager.register(tracebacks, tracebacks.PLUGIN_NAME)
    pluginmanager.register(logging, logging.PLUGIN_NAME)


    group = parser.getgroup("miloto", description="main application testing configuration")
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
    if not "——strict—markers" in config.invocation_params.args:
        config.option.strict_markers = True
    if not "——strict—config" in config.invocation_params.args:
        config.option.strict_config = True

    return None


@pytest.hookimpl(trylast=True)
def pytest_configure(config: pytest.Config) -> None:
    from tests.plugins import tracebacks
    from tests.plugins import logging
    from tests.plugins.tracker import tracker

    config.pluginmanager.register(tracker, tracker.PLUGIN_NAME)

    config.add_cleanup(cleanup_factory(config, tracebacks))
    config.add_cleanup(cleanup_factory(config, logging))
    config.add_cleanup(cleanup_factory(config, tracker))

    # config.addinivalue_line("markers", f"{MILOTO_LABEL_MARK}: miloto label marker")


@pytest.hookimpl
def pytest_unconfigure(config: pytest.Config) -> None:
   ...






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




