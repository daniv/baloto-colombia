# Project : baloto-colombia
# File Name : config.py
# Dir Path : src/baloto/core/config
# Created on: 2025–06–13 at 21:24:59.

from __future__ import annotations

import contextlib
from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field
from functools import cached_property
from pathlib import Path
from typing import Any
from typing import TYPE_CHECKING

import pluggy
from pydantic import ValidationError
from rich.console import Console

if TYPE_CHECKING:
    from baloto.core.richer.tracebacks import SysExceptionInfo
    from baloto.core.richer import RichSettings


class RichConfig:
    def __init__(self, settings: RichSettings, pluginmanager: pluggy.PluginManager) -> None:

        self.pluginmanager = pluginmanager
        self.hook: pluginmanager.hook
        self.trace = self.pluginmanager.trace.root.get("config")
        self.pluginmanager.register(self, "richconfig")
        self._configured = False
        self._cleanup_stack = contextlib.ExitStack()
        self.settings = settings

    @cached_property
    def pyproject(self) -> PyprojectInfo:
        from pydantic_settings import BaseSettings, SettingsConfigDict, TomlConfigSettingsSource
        from baloto.core.richer import locate

        file = locate("pyproject.toml")

        class Settings(BaseSettings):
            model_config = SettingsConfigDict(toml_file=file)

        toml = TomlConfigSettingsSource(Settings)
        return PyprojectInfo(data=toml.toml_data, path=Path(toml.toml_file_path).resolve())

    def add_cleanup(self, func: Callable[[], None]) -> None:
        self._cleanup_stack.callback(func)

    def do_configure(self) -> None:
        assert not self._configured
        self._configured = True
        self.pluginmanager.hook.rich_configure.call_historic(kwargs=dict(config=self))
        self.pluginmanager.hook.rich_provide_console.call_historic(
            kwargs=dict(console=self._get_console())
        )

    def _get_console(self) -> Console:
        return _get_console(self)

    def get_error_console(self) -> Console:
        return _get_console(self, True)

    def notify_exception(self, excinfo: SysExceptionInfo[BaseException]) -> None:
        res = self.pluginmanager.hook.rich_internalerror(excinfo=excinfo)
        if not any(res):
            console = self.get_error_console()
            console.print(res)

    def ensure_unconfigure(self) -> None:
        try:
            if self._configured:
                self._configured = False
                try:
                    self.pluginmanager.hook.rich_unconfigure(config=self)
                finally:
                    self.pluginmanager.hook.rich_configure._call_history = []
        finally:
            try:
                self._cleanup_stack.close()
            finally:
                self._cleanup_stack = contextlib.ExitStack()

    @staticmethod
    def init() -> RichConfig:
        from baloto.core.richer import console_factory
        from baloto.core.richer.logging import lib as logging_lib
        from baloto.core.richer.formatters import lib as formatters_lib
        from baloto.core.richer import RichPluginManager, RichSettings

        default_plugins = [
            (console_factory, "console-factory"),
            (logging_lib, "rich-logging"),
            (formatters_lib, "rich-formatters"),
        ]
        config = None
        try:
            pluginmanager = RichPluginManager.get_plugin_manager()
            config = RichConfig(RichSettings(), pluginmanager)
            pluginmanager = config.pluginmanager
            for plugin, name in default_plugins:
                pluginmanager.register(plugin, name)
                from baloto.core.richer import cleanup_factory

                config.add_cleanup(cleanup_factory(plugin))
            return config

        except (ValidationError, RichUsageError, Exception) as err:
            if isinstance(err, ValidationError):
                from rich import print
                from baloto.core.richer.formatters.validation_error import validation_error_renderer

                print(validation_error_renderer(err))
            else:
                from rich import get_console

                get_console().print_exception(show_locals=True, theme="ansi_dark")
                if config is not None:
                    config.ensure_unconfigure()
            raise err from err
