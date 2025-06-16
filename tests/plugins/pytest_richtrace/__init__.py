# Project : baloto-colombia
# File Name : __init__.py
# Dir Path : tests/plugins/pytest_richtrace
# Created on: 2025–06–14 at 14:27:57.
# Package :

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest


if TYPE_CHECKING:
    PytestPlugin = object

__all__ = [
    "PytestPlugin",
    "cleanup_factory",
]


def cleanup_factory(pluginmanager: pytest.PytestPluginManager, plugin: PytestPlugin):
    def clean_up() -> None:
        name = pluginmanager.get_name(plugin)
        # TODO: log message
        pluginmanager.unregister(name=name)

    return clean_up


class NotTest:
    def __init_subclass__(cls):
        cls.__test__ = NotTest not in cls.__bases__
