# Project : baloto-colombia
# File Name : lib.py
# Dir Path : src/baloto/core/rich/tracebacks
# Created on: 2025–06–13 at 23:09:40.

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from baloto.core.config.config import RichConfig

__all__ = ()


def rich_configure(config: RichConfig) -> None:
    from baloto.core.rich.formatters.theme import BalotoSyntaxTheme
    from baloto.core.rich.formatters.theme import BalotoTheme
    from baloto.core.rich.formatters.highlighter import BalotoHighlighter

    config.settings.syntax_theme = BalotoSyntaxTheme()
    config.settings.theme = BalotoTheme()
    config.settings.highlighter = BalotoHighlighter()
