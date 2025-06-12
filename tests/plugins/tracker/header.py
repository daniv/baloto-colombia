# Project : baloto-colombia
# File Name : header.py
# Dir Path : tests/plugins/tracker
# Created on: 2025–06–11 at 13:05:29.

from __future__ import annotations

import inspect
import sys
from argparse import Namespace
from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Any
from typing import Self
from typing import TYPE_CHECKING
from typing import TypedDict

import pytest
from glom import glom
from pydantic import BaseModel, field_validator
from pydantic import Field
from pydantic import FilePath
from pydantic import TypeAdapter
from pydantic import ValidationError
from pydantic_settings.sources.providers.toml import tomli
from rich.console import WINDOWS

if TYPE_CHECKING:
    pass

__all__ = ("build_environment", "RegisteredPluginInfo", "PytestEnvironment")


class RegisteredPluginInfo(BaseModel):
    name: str
    project_name: str
    version: str
    location: str
    cannonicalname: str


class ActivePluginInfo(BaseModel):
    project_name: str
    pack_or_class: str
    location: str | None = None


class PluginsInfo(BaseModel):
    registered_title: str | None = None
    active_title: str
    registered_plugins: list[RegisteredPluginInfo] = Field(default_factory=list)
    active_plugins: list[ActivePluginInfo] = Field(default_factory=list)


class PytestEnvironment(BaseModel, arbitrary_types_allowed=True):
    rootpath: str
    platform: str
    python_ver_info: str
    poetry: dict[str, str]
    configfile: str | None = None
    python: str | None = None
    pypy: str | None = None
    testpaths: list[str] = Field(default_factory=list)
    executable: str | None = None
    cache_dir: str | None = None
    pytest_ver: str | None = None
    plugins: PluginsInfo | None = None
    oprions: Namespace | None = None


def build_environment(config: pytest.Config) -> PytestEnvironment:
    import tomllib

    with open(config.inipath, "rb") as poetry_file:
        data = tomllib.load(poetry_file)

    import platform

    environment = PytestEnvironment(
        rootpath=config.rootpath.as_posix(),
        platform=sys.platform,
        python_ver_info=platform.python_version(),
        poetry={
            "name": glom(data, "project.name", default=""),
            "version": glom(data, "project.version", default=""),
            "description": glom(data, "project.description", default=""),
            "license": glom(data, "project.license.text", default=""),
            "requires-python": glom(data, "requires-python", default=""),
            "repo": glom(data, "urls.Repository", default=""),
        },
    )
    environment.python = ".".join(map(str, sys.version_info))

    # -- adding pypy_version_info idf available
    pypy_version_info = getattr(sys, "pypy_version_info", None)
    if pypy_version_info:
        verinfo = ".".join(map(str, pypy_version_info[:3]))
        environment.pypy = f"{verinfo} - {pypy_version_info[3]}"

    # -- adding configured test paths
    if config.args_source == pytest.Config.ArgsSource.TESTPATHS:
        testpaths: list[str] = config.getini("testpaths")
        environment.testpaths = ", ".join(testpaths)

    # -- adding python executable path
    executable = get_executable(config.option, config.rootpath)
    if executable:
        environment.executable = Path(sys.executable).relative_to(config.rootpath).as_posix()

    # -- adding cache dir
    displaypath = cache_dir(config)
    if displaypath:
        environment.cache_dir = str(displaypath)

    # -- adding registered plugins dist info
    plugins_info = PluginsInfo(
        registered_title="registered third-party plugins", active_title="active plugins"
    )
    plugin_distinfo = list_plugin_distinfo(config)
    plugins_info.registered_plugins = plugin_distinfo

    # -- adding pytest version if traceconfig was set or is debug mode
    if config.option.debug or config.option.traceconfig:
        environment.pytest_ver = str(pytest.__version__)

        # -- adding active plugins info if traceconfig was set or is debug mode
        name_plugins = list_name_plugin(config)
        plugins_info.active_plugins = name_plugins

    environment.plugins = plugins_info

    lines = config.hook.pytest_report_header(config=config, start_path=config.rootpath)
    for k, v in lines[-1]:
        if k == "configfile":
            environment.configfile = v
        elif k == "testpaths":
            environment.testpaths = v

    return environment


def list_plugin_distinfo(config: pytest.Config) -> list[RegisteredPluginInfo]:
    dist_list: list[RegisteredPluginInfo] = []

    plugininfo = config.pluginmanager.list_plugin_distinfo()
    if plugininfo:
        for plugin, dist in plugininfo:
            loc = getattr(plugin, "__file__", repr(plugin))
            relative = Path(loc).relative_to(config.rootpath).as_posix()
            plugin_info = RegisteredPluginInfo(
                cannonicalname=config.pluginmanager.get_canonical_name(plugin),
                name=dist.name,
                project_name=dist.project_name,
                version=dist.version,
                location=relative,
            )
            dist_list.append(plugin_info)
    return dist_list


def list_name_plugin(config: pytest.Config) -> list[ActivePluginInfo]:
    active_list: list[ActivePluginInfo] = []

    items = config.pluginmanager.list_name_plugin()

    for name, plugin in items:
        if plugin is None:
            continue
        if len(name) > 20:
            try:
                TypeAdapter(FilePath).validate_python(name)
                name = Path(name).relative_to(config.rootpath).as_posix()
            except ValidationError:
                pass
        mod = inspect.getmodule(plugin)
        if hasattr(plugin, "__file__"):
            path_file = Path(mod.__file__).relative_to(config.rootpath).as_posix()
            if path_file.find("site-packages"):
                path_file = path_file.replace("Lib/site-packages", "∼")
        pack = f"{mod.__name__}.{plugin.__class__.__name__}"
        plugin_info = ActivePluginInfo(
            project_name=name, pack_or_class=pack, location=locals().get("path_file")
        )
        active_list.append(plugin_info)

    return active_list


def cache_dir(config: pytest.Config) -> str | None:
    if config.option.verbose > 0 or config.getini("cache_dir") != ".pytest_cache":
        assert config.cache is not None
        try:
            displaypath = config.cache._cachedir.relative_to(config.rootpath)
        except ValueError:
            displaypath = config.cache._cachedir
        return str(displaypath)
    return None


def get_executable(option: Namespace, rootpath: Path) -> str | None:
    if option.verbose > 0 or option.debug or getattr(option, "pastebin", None):
        return Path(sys.executable).relative_to(rootpath).as_posix()
    return None
