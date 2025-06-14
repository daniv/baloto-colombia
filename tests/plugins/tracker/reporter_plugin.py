# Project : baloto-colombia
# File Name : reporter_plugin.py
# Dir Path : tests/plugins/tracker
# Created on: 2025–06–13 at 04:28:22.

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from rich.console import Console


__all__ = ("ReporterPlugin", )


class ReporterPlugin:
    def __init__(self, config: pytest.Config, console: Console) -> None:
        self.config = config
        self.console = console