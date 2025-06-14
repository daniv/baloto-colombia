# — Project : baloto-colombia
# — File Name : __init__.py
# — Dir Path : tests/plugins/error_reporter
# — Created on: 2025–06–04 at 12:32:34.

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

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
    # TODO: unregister the plugin "terminal" cause issues with other plugins
    # setattr config
    if plugin_name in ["terminalreporter"]:
        if hasattr(plugin, "name"):
            if getattr(plugin, "name", None) == TrackerPlugin.name:
                return

        config = getattr(plugin, "config")

        tracker_plugin = TrackerPlugin(config)
        manager.unregister(plugin=plugin)
        config.pluginmanager.register(tracker_plugin, "terminalreporter")


# @pytest.hookimpl
# def pytest_configure(config: pytest.Config) -> None:
#     from tests import get_console_key, create_console_from_key
#
#     console_key = get_console_key()
#     console = config.stash.get(console_key, None)
#     if console is None:
#         create_console_from_key(config)