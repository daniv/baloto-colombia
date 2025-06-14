# Project : baloto-colombia
# File Name : collection_observer.py
# Dir Path : tests/plugins/tracker
# Created on: 2025–06–12 at 23:27:28.

from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from typing import TYPE_CHECKING

import pytest

from baloto.core.tester.rich_testers import hookimpl

if TYPE_CHECKING:
    pass

__all__ = ("CollectionObserver", )


class CollectionObserver:
    def __init__(self) -> None:
        self.config: pytest.Config | None = None

    @hookimpl
    def rich_configure(self, config: pytest.Config, poetry: Mapping[str, Any]) -> None:
        self.config = config
