# — Project : baloto-colombia
# — File Name : __init__.py
# — Dir Path : tests/plugins/error_reporter
# — Created on: 2025–06–04 at 12:32:34.

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from baloto.core.config.settings import settings
from helpers import cleanup_factory
from plugins.tracker.tracker import TrackerPlugin

if TYPE_CHECKING:
    pass

__all__ = ()

PLUGIN_NAME = "baloto-tracker"
_PluggyPlugin = object


@pytest.hookimpl
def pytest_plugin_registered(
    plugin: _PluggyPlugin,
    plugin_name: str,
    manager: pytest.PytestPluginManager,
) -> None:
    if plugin_name == "terminalreporter":
        if hasattr(plugin, "name"):
            if getattr(plugin, "name", None) == TrackerPlugin.name:
                return

        config = getattr(plugin, "config")

        tracker_plugin = TrackerPlugin(config)
        manager.unregister(plugin=plugin)
        config.pluginmanager.register(tracker_plugin, "terminalreporter")
        config.add_cleanup(cleanup_factory(config, tracker_plugin))
