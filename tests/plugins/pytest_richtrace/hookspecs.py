# Project : baloto-colombia
# File Name : hookspecs.py
# Dir Path : tests/plugins/pytest_richtrace
# Created on: 2025–06–14 at 14:39:25.

from __future__ import annotations

from typing import Any
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections import ChainMap
    from rich.console import Console
    from baloto.core.richer import RichSettings


@pytest.hookspec(historic=True)
def pytest_console_and_settings(console: Console, settings: RichSettings) -> None:
    """Provides the framework settings and the rich console,

    :param console: The rich.Console instance
    :param settings: The configuration settings
    :return: a dictionary with the information collected
    """


@pytest.hookspec
def pytest_collect_env_info(config: pytest.Config) -> dict[str, Any]:
    """Collects environment information for the header,

    :param config: The pytest config
    :return: a dictionary with the information collected
    """
    pass


class ReportingHookSpecs:

    @pytest.hookspec
    def pytest_report_sessionstart(self, session: pytest.Session) -> None:
        pass

    @pytest.hookspec(firstresult=True)
    def pytest_render_header(self, config: pytest.Config, data: ChainMap) -> bool:
        pass

    @pytest.hookspec
    def pytest_report_collectreport(self, report: pytest.CollectReport) -> None:
        pass

    @pytest.hookspec#(firstresult=True)
    def pytest_report_make_collect_report(self, collector: pytest.Collector) -> None:
        pass



