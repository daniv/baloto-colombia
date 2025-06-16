# Project : baloto-colombia
# File Name : test_execution_observer.py
# Dir Path : tests/plugins/pytest_richtrace
# Created on: 2025–06–14 at 18:43:12.
# Package :

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from rich.console import Console
    from baloto.core.richer import RichSettings
    from plugins.pytest_richtrace.models import TestRunResults


class TestExecutionObserver:

    name = "richtrace-testrun"
    test_run_results: TestRunResults

    def __init__(self, config: pytest.Config, results: TestRunResults):
        self.config = config
        self.test_run_results = results
        self.console: Console | None = None
        self.settings: RichSettings | None = None
        self._started = False

    def pytest_console_and_settings(self, console: Console, settings: RichSettings) -> None:
        self.settings = settings
        self.console = console

    @pytest.hookimpl
    def pytest_configure(self, config: pytest.Config) -> None:
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} " f"name='{self.name}' " f"started={self._started!r}>"
