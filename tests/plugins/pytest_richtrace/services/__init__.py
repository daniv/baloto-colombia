# Project : baloto-colombia
# File Name : __init__.py
# Dir Path : tests/plugins/pytest_richtrace/services
# Created on: 2025–06–15 at 00:50:06.
# Package :

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel
from pydantic import Field
from pydantic import InstanceOf

if TYPE_CHECKING:
    pass


# class ActivePluginInfo(BaseModel):
#     name: str
#     pack_or_class: str | None = None
#     location: str | None = None
#
#
# class RegisteredPluginInfo(ActivePluginInfo):
#     project_name: str
#     version: str
#     cannonicalname: str
#
# class PluginsInfo(BaseModel):
#     registered_title: str | None = None
#     active_title: str
#     registered_plugins: list[InstanceOf[RegisteredPluginInfo]] = Field(default_factory=list)
#     active_plugins: list[InstanceOf[ActivePluginInfo]] = Field(default_factory=list)
