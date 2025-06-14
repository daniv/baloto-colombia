# Project : baloto-colombia
# File Name : host.py
# Dir Path : src/baloto/core/config
# Created on: 2025–06–13 at 21:24:07.

from __future__ import annotations

from typing import TYPE_CHECKING

import pluggy

from baloto.core.config import hookspecs

if TYPE_CHECKING:
    pass

__all__ = ("RichPluginManager",)


class RichPluginManager(type):
    plugin_manager: pluggy.PluginManager = None

    @staticmethod
    def get_plugin_manager():
        if not RichPluginManager.plugin_manager:
            RichPluginManager.plugin_manager = pluggy.PluginManager("rich")
            RichPluginManager.plugin_manager.add_hookspecs(hookspecs.RichSpecs)
            RichPluginManager.plugin_manager.load_setuptools_entrypoints("rich")
            from baloto.core.rich.logging import lib

            RichPluginManager.plugin_manager.register(lib, name="rich-logging")

        return RichPluginManager.plugin_manager

    def __getattr__(cls, attr):
        pm = RichPluginManager.get_plugin_manager()
        return getattr(pm, attr)
