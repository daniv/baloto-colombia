# Project : baloto-colombia
# File Name : text_execution_plugin.py
# Dir Path : tests/plugins/tracker
# Created on: 2025–06–13 at 04:27:48.

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    pass

__all__ = ("TestExecutionObserver", )


class TestExecutionObserver:
    def __init__(self) -> None:
        self.config: pytest.Config | None = None