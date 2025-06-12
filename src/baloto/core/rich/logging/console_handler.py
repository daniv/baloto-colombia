from __future__ import annotations

import logging
from types import ModuleType
from typing import Any
from collections.abc import Callable
from typing import Iterable
from typing import TYPE_CHECKING

import pendulum
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import computed_field
from pydantic import field_validator
from rich._null_file import NullFile
from rich.logging import RichHandler
from rich.text import Text

from baloto.cleo.io.outputs.output import Verbosity

if TYPE_CHECKING:
    from logging import LogRecord
    from rich.console import Console
    from rich.highlighter import Highlighter

    FormatTimeCallable = Callable[[pendulum.DateTime], Text]

__all__ = "ConsoleHandler"

class ConsoleHandler(RichHandler):
    def __init__(
        self,
        level: int | str = logging.NOTSET,
        console: Console | None = None,
        *,
        show_time: bool = True,
        omit_repeated_times: bool = True,
        show_level: bool = True,
        show_path: bool = True,
        enable_link_path: bool = True,
        highlighter: Highlighter | None = None,
        markup: bool = False,
        rich_tracebacks: bool = False,
        tracebacks_width: int | None = None,
        tracebacks_code_width: int = 88,
        tracebacks_extra_lines: int = 3,
        tracebacks_theme: str | None = None,
        tracebacks_word_wrap: bool = True,
        tracebacks_show_locals: bool = False,
        tracebacks_suppress: Iterable[str | ModuleType] = (),
        tracebacks_max_frames: int = 100,
        locals_max_length: int = 10,
        locals_max_string: int = 80,
        keywords: list[str] | None = None,
    ) -> None:

        super().__init__(
            level,
            console,
            show_time=show_time,
            omit_repeated_times=omit_repeated_times,
            show_level=show_level,
            show_path=show_path,
            enable_link_path=enable_link_path,
            highlighter=highlighter,
            markup=markup,
            rich_tracebacks=rich_tracebacks,
            tracebacks_width=tracebacks_width,
            tracebacks_code_width=tracebacks_code_width,
            tracebacks_extra_lines=tracebacks_extra_lines,
            tracebacks_theme=tracebacks_theme,
            tracebacks_word_wrap=tracebacks_word_wrap,
            tracebacks_show_locals=tracebacks_show_locals,
            tracebacks_suppress=tracebacks_suppress,
            tracebacks_max_frames=tracebacks_max_frames,
            locals_max_length=locals_max_length,
            locals_max_string=locals_max_string,
            keywords=keywords
        )

        from baloto.core.rich.logging.log_render import ConsoleLogRender
        self._log_render = ConsoleLogRender(show_time=False, show_level=True)

    def emit(self, record: LogRecord) -> None:

        if isinstance(self.console.file, NullFile):
            return None

        message = self.format(record)
        traceback = None
        if self.rich_tracebacks and record.exc_info and record.exc_info != (None, None, None):
            exc_type, exc_value, exc_traceback = record.exc_info
            assert exc_type is not None
            assert exc_value is not None
            from baloto.core.rich.tracebacks import RichTraceback
            traceback = RichTraceback.from_exception(
                exc_type,
                exc_value,
                exc_traceback,
                width=self.tracebacks_width,
                code_width=self.tracebacks_code_width,
                extra_lines=self.tracebacks_extra_lines,
                theme=self.tracebacks_theme,
                word_wrap=self.tracebacks_word_wrap,
                show_locals=self.tracebacks_show_locals,
                locals_max_length=self.locals_max_length,
                locals_max_string=self.locals_max_string,
                suppress=self.tracebacks_suppress,
                max_frames=self.tracebacks_max_frames,
            )
            message = record.getMessage()
            if self.formatter:
                record.message = record.getMessage()
                formatter = self.formatter
                if hasattr(formatter, "usesTime") and formatter.usesTime():
                    record.asctime = formatter.formatTime(record, formatter.datefmt)
                message = formatter.formatMessage(record)

        message_renderable = self.render_message(record, message)
        log_renderable = self.render(record=record, traceback=traceback, message_renderable=message_renderable)
        try:
            self.console.print(log_renderable)
        except Exception as e:
            self.handleError(record)

    def get_level_text(self, record: LogRecord) -> Text:
        level_name = record.levelname
        level_text = Text.styled(level_name.lower().ljust(8), f"logging.level.{level_name.lower()}")
        return level_text


# noinspection PyNestedDecorators
class TracebackPolicy(BaseModel):
    model_config = ConfigDict(extra="ignore", validate_assignment=True, arbitrary_types_allowed=True)

    verbosity: Verbosity
    logging_level: int = Field(default=logging.NOTSET, ge=logging.NOTSET, le=logging.CRITICAL)
    rich_tracebacks: bool = False
    tracebacks_show_locals: bool = False

    @computed_field()
    @property
    def tracebacks_max_frames(self) -> int:
        return 100

    def model_post_init(self, __context: Any) -> None: ...

    @field_validator("logging_level", mode="after")
    @classmethod
    def logging_level_values(cls, value: int) -> int:
        mappings = logging.getLevelNamesMapping()
        mappings = dict(filter(lambda key_value: key_value[0] not in ["WARN", "FATAL"], mappings.items()))
        values = list(mappings.values())

        if value not in values:
            names = list(mappings.keys())
            names_keys = list(zip(names, values))
            # TODO create console message

            raise ValueError(f"{value} is not definided on logging")
        return value
