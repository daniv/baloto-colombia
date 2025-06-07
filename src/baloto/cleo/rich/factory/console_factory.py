from __future__ import annotations

import sys
from io import StringIO
from typing import IO
from typing import TYPE_CHECKING

from rich._null_file import NullFile
from rich.console import Console
from rich.highlighter import NullHighlighter
from rich.highlighter import ReprHighlighter

from baloto.cleo.formatters.formatter import Formatter
from baloto.cleo.formatters.theme import MilotoTheme, MilotoHighlighter
from baloto.cleo.rich.logging.log_render import ConsoleLogRender

if TYPE_CHECKING:
    from rich.theme import Theme
    from rich.style import StyleType
    from rich.emoji import EmojiVariant
    from rich._log_render import FormatTimeCallable
    from rich.console import HighlighterType

_FALLBACK_COLUMNS = "254"
_FALLBACK_LINES = "14"

class ConsoleFactoryy:
    log_time_format: str | FormatTimeCallable = "[%X]",

    formatter: Formatter | None = None

    def __init__(
        self,
        *,
        force_terminal: bool | None = None,
        force_interactive: bool | None = None,
        soft_wrap: bool = False,
        theme: Theme | None = None,
        stderr: bool = False,
        file: IO[str] | None = None,
        quiet: bool = False,
        width: int | None = None,
        height: int | None = None,
        style: StyleType | None = None,
        no_color: bool | None = None,
        tab_size: int = 8,
        record: bool = False,
        markup: bool = True,
        emoji: bool = True,
        emoji_variant: EmojiVariant | None = None,
        highlight: bool = True,
        highlighter: HighlighterType | None = ReprHighlighter(),
        legacy_windows: bool | None = None,
        safe_box: bool = True,
        environ: dict[str, str] | None = None,
    ) -> None:

        self.console = Console(
            color_system="truecolor",
            force_interactive=force_interactive,
            soft_wrap=soft_wrap,
            file=file,
            theme=theme,
            stderr=stderr,
            width=width,
            height=height,
            style=style,
            no_color=no_color,
            markup=markup,
            emoji=emoji,
            emoji_variant=emoji_variant,
            tab_size=tab_size,
            quiet=quiet,
            safe_box=safe_box,
            highlight=highlight,
            force_terminal=force_terminal,
            legacy_windows=legacy_windows,
            log_time=False,
            log_path=True,
            highlighter=highlighter,
            record=record,
            log_time_format="[%X]",
            _environ=environ
        )
        # render = getattr(self.console, "_log_render")
        # self.console._log_render = ConsoleLogRender(
        #     show_time=render.time_format,
        #     show_path=render.time_format,
        #     time_format=render.time_format,
        # )

    @staticmethod
    def isatty() -> bool:
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

    @classmethod
    def console_output(cls, soft_wrap: bool = True, **kwargs) -> Console:
        environ = {}
        legacy_windows = None

        if not cls.is_isatty():
            legacy_windows = False
            environ = {"COLUMNS":_FALLBACK_COLUMNS, "LINES":_FALLBACK_LINES}

        data = dict(
            force_terminal=True,
            force_interactive=True,
            legacy_windows=legacy_windows,
            soft_wrap=soft_wrap,
            environ=environ,
            highlighter=MilotoHighlighter(),
            theme=MilotoTheme().styles,
        )

        kwargs.update(data)
        console = cls(**kwargs).console

        return console

    @classmethod
    def console_error_output(cls, soft_wrap: bool = True) -> Console:
        environ = {}
        legacy_windows = None
        if not cls.is_isatty():
            legacy_windows = False
            environ = {"COLUMNS":_FALLBACK_COLUMNS, "LINES":_FALLBACK_LINES}

        return cls(
            stderr=True,
            force_terminal=True,
            legacy_windows=legacy_windows,
            force_interactive=False,
            style="bold red",
            soft_wrap=soft_wrap,
            highlighter=MilotoHighlighter(),
            theme=MilotoTheme(),
            environ=environ
        ).console

    @classmethod
    def null_file(cls) -> Console:
        return cls(file=NullFile(), highlight=False, quiet=True).console

    @classmethod
    def console_output_string_io(cls) -> Console:
        console = cls.console_output(soft_wrap=False)
        console.file = StringIO()
        return console

    @classmethod
    def console_no_color_string_io(cls) -> Console:
        from rich.style import NULL_STYLE

        return cls(
            file=StringIO(),
            highlight=False,
            legacy_windows=True,
            force_terminal=False,
            markup=False,
            highlighter=NullHighlighter(),
            no_color=True,
            style=NULL_STYLE,
        ).console


