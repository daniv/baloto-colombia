# Project : baloto-colombia
# File Name : __init__.py
# Dir Path : src/baloto/core/rich
# Created on: 2025–06–10 at 22:47:13.

from __future__ import annotations

from baloto.core.richer.config.config import RichConfig
from baloto.core.richer.logging.console_logger import MessagePrefixEnum
from baloto.core.richer.logging.lib import setup_logging
from baloto.core.richer.settings import get_rich_settings
from baloto.core.richer.stash import RichStashKey
from baloto.core.richer.console_factory import ConsoleFactory
from baloto.core.richer.formatters.highlighter import RichHighlighter
from baloto.core.richer.formatters.theme import RichSyntaxTheme
from baloto.core.richer.formatters.theme import RichTheme
from baloto.core.richer.formatters.tracebacks import RichTraceback
from baloto.core.richer.formatters.tracebacks import SysExceptionInfo
from baloto.core.richer.formatters.validation_error import validation_error_renderer
from baloto.core.richer.logging.console_handler import ConsoleHandler
from baloto.core.richer.logging.lib import RichLogging
from baloto.core.richer.logging.log_render import ConsoleLogRender
from baloto.core.richer.section_message import SectionMessages
from baloto.core.richer.settings import ConsoleSettings
from baloto.core.richer.settings import RichSettings
from baloto.core.richer.settings import locate

RichPlugin = object

__all__ = [
    "RichLogging",
    "RichPlugin",
    "RichConfig",
    "RichSettings",
    "locate",
    "ConsoleSettings",
    "SectionMessages",
    "RichTheme",
    "RichSyntaxTheme",
    "RichHighlighter",
    "RichTraceback",
    "ConsoleLogRender",
    "RichUsageError",
    "validation_error_renderer",
    "SysExceptionInfo",
    "ConsoleFactory",
    "ConsoleHandler",
    "RichStashKey",
    "MessagePrefixEnum",
    "setup_logging",
    "get_rich_settings",
]


class RichUsageError(Exception):
    pass
