# Project : baloto-colombia
# File Name : config.py
# Dir Path : src/baloto/core/config
# Created on: 2025–06–13 at 21:24:59.

from __future__ import annotations

import contextlib
import enum
from collections.abc import Callable
from collections.abc import Sequence
from dataclasses import dataclass
from dataclasses import field
from functools import cached_property
from typing import Any
from typing import TYPE_CHECKING

import pluggy
from pydantic import ValidationError
from rich.console import Console

from baloto.core.config import RichUsageError
from baloto.core.config import stash
from baloto.core.config.host import RichPluginManager
from baloto.core.config.settings import RichSettings
from baloto.core.config.stash import RichStash
from baloto.core.rich.console_factory import ConsoleFactory

if TYPE_CHECKING:
    from baloto.core.rich.tracebacks import SysExceptionInfo
    from pathlib import Path

__all__ = ("ExitCode", "RichPlugin", "RichConfig", "RichStash", "RichPluginManager")

RichPlugin = object
console_key = stash.RichStashKey[Console]()
eror_console_key = stash.RichStashKey[Console]()


@enum.unique
class ExitCode(enum.IntEnum):
    SUCCESS = 0
    FAILURE = 1
    INTERRUPTED = 2
    INTERNAL_ERROR = 3
    USAGE_ERROR = 4


default_plugins = "tracebacks"


@dataclass
class PyprojectInfo:
    path: Path
    data: dict[str, Any] = field(default_factory=dict)


def get_console_key(config: RichConfig, error: bool = False) -> Console:

    if error:
        console = config.stash.get(eror_console_key, None)
        if console is None:
            return _create_console_from_key(config, True)
    else:
        console = config.stash.get(console_key, None)
        if console is None:
            return _create_console_from_key(config)


def _create_console_from_key(config: RichConfig, error: bool = False) -> Console:
    from baloto.core.rich.console_factory import ConsoleFactory

    if error:
        console = ConsoleFactory.console_error_output()
        config.stash.setdefault(eror_console_key, console)
        return config.stash.get(eror_console_key, None)

    console = ConsoleFactory.console_output()
    config.stash.setdefault(console_key, console)
    return config.stash.get(console_key, None)


class RichConfig:
    def __init__(self, settings: RichSettings, pluginmanager: pluggy.PluginManager) -> None:
        self.pluginmanager = pluginmanager
        self.stash = RichStash()
        self.trace = self.pluginmanager.trace.root.get("config")
        self.pluginmanager.register(self, "richconfig")
        self._configured = False
        self._cleanup_stack = contextlib.ExitStack()
        self.settings = settings

    @cached_property
    def rootpath(self) -> Path:
        return self.pyproject.path

    @cached_property
    def pyproject(self) -> PyprojectInfo:
        from pydantic_settings import BaseSettings, SettingsConfigDict, TomlConfigSettingsSource
        from baloto.core.config.settings import locate

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
        self.pluginmanager.rich_configure.call_historic(kwargs=dict(config=self))

    def get_console(self) -> Console:
        return get_console_key(self)

    def get_error_console(self) -> Console:
        return get_console_key(self, True)

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
                    self.pluginmanager.rich_unconfigure(config=self)
                finally:
                    self.pluginmanager.rich_configure._call_history = []
        finally:
            try:
                self._cleanup_stack.close()
            finally:
                self._cleanup_stack = contextlib.ExitStack()


def main(
    plugins: Sequence[str | RichPlugin] | None = None,
):
    config = None
    try:
        config = _prepareconfig(plugins)
    except (ValidationError, RichUsageError) as err:
        if isinstance(err, ValidationError):
            # TODO: ValidationError Report with Group of Frames
            pass

        console = ConsoleFactory.console_error_output()
        console.print_exception()
        return ExitCode.USAGE_ERROR
    finally:
        if config is not None:
            config.ensure_unconfigure()
        return ExitCode.USAGE_ERROR


def _prepareconfig(
    plugins: Sequence[str | RichPlugin] | None = None,
) -> RichConfig:
    config = get_config()
    pluginmanager = config.pluginmanager
    try:
        if plugins:
            for plugin in plugins:
                if isinstance(plugin, str):
                    pluginmanager.consider_pluginarg(plugin)
                else:
                    pluginmanager.register(plugin)
        return config
    except BaseException:
        config.ensure_unconfigure()
        raise


def get_config() -> RichConfig:
    pluginmanager = RichPluginManager.get_plugin_manager()
    try:
        settings = RichSettings()
        config = RichConfig(settings, pluginmanager)
        for spec in default_plugins:
            pluginmanager.import_plugin(spec)
    except ValidationError as err:
        errors = err.errors()
        raise

    return config
