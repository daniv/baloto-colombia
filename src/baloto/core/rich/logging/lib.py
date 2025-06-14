# Project : baloto-colombia
# File Name : logging_lib.py
# Dir Path : src/baloto/core/rich/logging
# Created on: 2025–06–13 at 21:38:04.

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from baloto.core.config import RichUsageError
from baloto.core.config import cleanup_factory
from baloto.core.config import hookimpl

if TYPE_CHECKING:
    from baloto.core.config.config import RichConfig

__all__ = ("RichLoggingPlugin",)


def rich_configure(config: RichConfig) -> None:
    plugin = RichLoggingPlugin(config)
    config.pluginmanager.register(plugin, "rich-logging-handler")
    config.add_cleanup(cleanup_factory(plugin))


class RichLoggingPlugin:
    def __init__(self, config: RichConfig) -> None:
        self.config = config
        self.log_file_handler: logging.FileHandler | None = None

        settings = config.settings

        self.handler_options = dict(
            show_time=settings.logging.show_time,
            omit_repeated_times=settings.logging.omit_repeated_times,
            show_level=settings.logging.show_level,
            show_path=settings.logging.show_path,
            enable_link_path=settings.logging.enable_link_path,
            highlighter=settings.console.highlighter,
            markup=settings.logging.markup,
            rich_tracebacks=settings.logging.rich_tracebacks,
            tracebacks_extra_lines=settings.tracebacks.extra_lines,
            tracebacks_theme=settings.console.theme,
            tracebacks_show_locals=settings.tracebacks.show_locals,
            tracebacks_max_frames=settings.tracebacks.max_frames,
            keywords=settings.logging.keywords,
        )

    @staticmethod
    def reset_logging() -> None:
        # -- Remove all handlers from the root logger
        root = logging.getLogger()
        for h in root.handlers[:]:
            root.removeHandler(h)
        # -- Reset logger hierarchy, this clears the internal dict of loggers
        logging.Logger.manager.loggerDict.clear()

    @hookimpl
    def rich_configure(self, config: RichConfig) -> None:

        log_level = self.config.settings.logging.log_level
        if isinstance(log_level, str):
            log_level = logging.getLevelName(log_level)
        try:
            from baloto.core.rich.logging.console_handler import ConsoleHandler

            console = config.get_console()
            if not console.file.isatty():
                config.settings.isatty_link = False
            rich_handler = ConsoleHandler(log_level, console, **self.handler_options)

        except ValueError as e:
            if str(e).startswith("Unknown level"):
                raise RichUsageError(
                    f"'{log_level}' is not recognized as a logging level name for "
                    f"'log_level'. Please consider passing the logging level num instead."
                ) from e
            raise e from e

        def reset_logging() -> None:
            # -- Remove all handlers from the root logger
            root = logging.getLogger()
            for h in root.handlers[:]:
                root.removeHandler(h)
            # -- Reset logger hierarchy, this clears the internal dict of loggers
            logging.Logger.manager.loggerDict.clear()

        log_format = config.settings.logging.log_format
        log_date_format = config.settings.logging.log_date_format

        config.add_cleanup(reset_logging)
        reset_logging()
        logging.basicConfig(
            level=logging.NOTSET,
            format=log_format,
            datefmt=log_date_format,
            handlers=[rich_handler],
        )
        logging.captureWarnings(True)

    @hookimpl
    def rich_unconfigure(self) -> None:
        self.reset_logging()
        if self.log_file_handler:
            self.log_file_handler.close()
