from __future__ import annotations

from collections.abc import Callable
from collections.abc import Mapping
from datetime import datetime
from io import StringIO
from typing import IO
from typing import Literal
from typing import TYPE_CHECKING

from rich._null_file import NullFile
from rich.console import Console
from rich.highlighter import NullHighlighter
from rich.highlighter import ReprHighlighter

from baloto.cleo.formatters.formatter import Formatter

if TYPE_CHECKING:
    from rich.theme import Theme
    from rich.style import StyleType
    from rich.emoji import EmojiVariant
    from rich._log_render import FormatTimeCallable
    from rich.console import HighlighterType


class ConsoleFactory:

    formatter: Formatter | None = None

    def __init__(
        self,
        *,
        color_system: None | Literal["auto", "standard", "256", "truecolor", "windows"] = "auto",
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
        log_time: bool = True,
        log_path: bool = True,
        log_time_format: str | FormatTimeCallable = "[%X]",
        highlighter: HighlighterType | None = ReprHighlighter(),
        legacy_windows: bool | None = None,
        safe_box: bool = True,
        get_datetime: Callable[[], datetime] | None = None,
        get_time: Callable[[], float] | None = None,
        _environ: Mapping[str, str] | None = None,
    ) -> None:
        self.console = Console(
            color_system=color_system,
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
            log_time=log_time,
            log_path=log_path,
            highlighter=highlighter,
            record=record,
            log_time_format=log_time_format,
            get_time=get_time,
            get_datetime=get_datetime,
        )

    @classmethod
    def console_output(cls, soft_wrap: bool = True) -> Console:
        console = cls(
            force_terminal=True,
            highlight=True,
            soft_wrap=soft_wrap,
            force_interactive=True,
            theme=ConsoleFactory.default_theme(),
        ).console
        from baloto.cleo.rich.logging.log_render import ConsoleLogRender

        render = console._log_render
        console._log_render = ConsoleLogRender(
            show_time=False,
            show_path=True,
            time_format=render.time_format,
        )

        return console


    @classmethod
    def console_error_output(cls, soft_wrap: bool = True) -> Console:
        return cls(
            stderr=True,
            style="bold red",
            force_terminal=True,
            highlight=True,
            soft_wrap=soft_wrap,
            force_interactive=False,
            theme=ConsoleFactory.default_theme(),
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
            markup=False,
            highlighter=NullHighlighter(),
            no_color=True,
            style=NULL_STYLE,
        ).console

    @classmethod
    def default_theme(cls) -> Theme:
        if cls.formatter is None:
            import warnings
            warnings.warn("The formatter was not set! the rich.Theme will be the default", RuntimeWarning, stacklevel=2)
            return Formatter().create_theme()
        return cls.formatter.create_theme()
