# Project : baloto-colombia
# File Name : __init__.py
# Dir Path : src/baloto/core/config
# Created on: 2025–06–10 at 22:42:40.

from __future__ import annotations

from typing import TYPE_CHECKING

from baloto.core.config import hookspecs

if TYPE_CHECKING:
    from baloto.core.config.config import RichPlugin

__all__ = ("hookimpl", "RichUsageError", "cleanup_factory")

import pluggy


hookimpl = pluggy.HookimplMarker("rich")


class RichUsageError(Exception):
    pass


def cleanup_factory(plugin: RichPlugin):
    def clean_up() -> None:
        from baloto.core.config.host import RichPluginManager

        plugin_manager = RichPluginManager.get_plugin_manager()
        name = plugin_manager.get_name(plugin)
        plugin_manager.unregister(name=name)

    return clean_up


# class pluginmanager(metaclass=RichPluginManager):
#     pass
