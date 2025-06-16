# Project : baloto-colombia
# File Name : logging_lib.py
# Dir Path : src/baloto/core/rich/logging
# Created on: 2025–06–13 at 21:38:04.

from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from baloto.core.richer.settings import get_rich_settings

if TYPE_CHECKING:
    from rich.console import Console
    from baloto.core.richer import RichSettings


def reset_logging() -> None:
    # -- Remove all handlers from the root logger
    root = logging.getLogger()
    for h in root.handlers[:]:
        root.removeHandler(h)
    # -- Reset logger hierarchy, this clears the internal dict of loggers
    logging.Logger.manager.loggerDict.clear()


class RichLogging:
    def __init__(self) -> None:

        settings = get_rich_settings()

        self.log_file_handler: logging.FileHandler | None = None
        self.handler_options = dict(
            show_time=settings.logging.show_time,
            omit_repeated_times=settings.logging.omit_repeated_times,
            show_level=settings.logging.show_level,
            show_path=settings.logging.show_path,
            enable_link_path=settings.logging.enable_link_path,
            highlighter=settings.highlighter,
            markup=settings.logging.markup,
            rich_tracebacks=settings.logging.rich_tracebacks,
            tracebacks_extra_lines=settings.tracebacks.extra_lines,
            tracebacks_theme=settings.theme,
            tracebacks_show_locals=settings.tracebacks.show_locals,
            tracebacks_max_frames=settings.tracebacks.max_frames,
            keywords=settings.logging.keywords,
        )

        from baloto.core.richer.console_factory import ConsoleFactory

        self._configure(ConsoleFactory.console_output(), settings)

    def _configure(self, console: Console, settings: RichSettings) -> None:

        rich_settings = get_rich_settings()
        log_level = rich_settings.logging.log_level
        if isinstance(log_level, str):
            log_level = logging.getLevelName(log_level)
        try:
            from baloto.core.richer.logging.console_handler import ConsoleHandler

            rich_handler = ConsoleHandler(log_level, console, **self.handler_options)

        except ValueError as e:
            if str(e).startswith("Unknown level"):
                from baloto.core.richer import RichUsageError

                raise RichUsageError(
                    f"'{log_level}' is not recognized as a logging level name for "
                    f"'log_level'. Please consider passing the logging level num instead."
                ) from e
            raise e from e

        log_format = settings.logging.log_format
        log_date_format = settings.logging.log_time_format

        reset_logging()
        logging.basicConfig(
            level=logging.NOTSET,
            format=log_format,
            datefmt=log_date_format,
            handlers=[rich_handler],
        )
        logging.captureWarnings(True)


def setup_logging() -> None:
    RichLogging()
