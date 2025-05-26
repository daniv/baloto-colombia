from __future__ import annotations

from collections.abc import Callable
from collections.abc import Mapping
from datetime import datetime
from typing import IO
from typing import Literal
from typing import TYPE_CHECKING, Self

from baloto.core.patterns.builder import Builder
from rich.console import Console

if TYPE_CHECKING:
    from rich.theme import Theme
    from rich.style import StyleType
    from rich.emoji import EmojiVariant
    from rich._log_render import FormatTimeCallable
    from rich.console import HighlighterType
    from rich.console import ConsoleDimensions


class ConsoleBuilder(Builder):
    __slots__ = "console"

    def __init__(
        self,
        *,
        color_system: None | Literal["auto", "standard", "256", "truecolor", "windows"] = "auto",
        markup: bool = True,
        emoji: bool = True,
        emoji_variant: EmojiVariant | None = None,
        highlight: bool = True,
        force_terminal: bool | None = None,
        theme: Theme | None = None,
        log_time: bool = True,
        log_path: bool = True,
        log_time_format: str | FormatTimeCallable = "[%X]",
    ) -> None:
        self.console = Console(
            color_system=color_system, theme=theme,
            markup=markup, emoji=emoji, emoji_variant=emoji_variant,
            highlight=highlight, force_terminal=force_terminal,
            log_time=log_time, log_path=log_path, log_time_format=log_time_format
        )

    def build(self) -> Console: # type: ignore[override]
        return self.console

    def file(self, new_file: IO[str]) -> Self:
        self.console.file = new_file
        return self

    def size(self, new_size: ConsoleDimensions) -> Self:
        self.console.size = new_size
        return self

    def width(self, width: int) -> Self:
        self.console.width = width
        return self

    def height(self, height: int) -> Self:
        self.console.height = height
        return self

    def force_interactive(self, interactive: bool) -> Self:
        self.console.is_interactive = interactive
        return self

    def soft_wrap(self, soft_wrap: bool) -> Self:
        self.console.soft_wrap = soft_wrap
        return self

    def stderr(self, stderr: bool) -> Self:
        self.console.stderr = stderr
        return self

    def quiet(self, quiet: bool) -> Self:
        self.console.quiet = quiet
        return self

    def no_color(self, no_color: bool) -> Self:
        self.console.no_color = no_color
        return self

    def record(self, record: bool) -> Self:
        self.console.record = record
        return self

    def legacy_windows(self, legacy_windows: bool) -> Self:
        self.console.legacy_windows = legacy_windows
        return self

    def safe_box(self, safe_box: bool) -> Self:
        self.console.safe_box = safe_box
        return self

    def tab_size(self, tab_size: int) -> Self:
        self.console.tab_size = tab_size
        return self

    def style(self, style: StyleType) -> Self:
        self.console.style = style
        return self

    def highlighter(self, highlighter: HighlighterType) -> Self:
        self.console.highlighter = highlighter
        return self

    def get_datetime_calleble(self, get_datetime: Callable[[], datetime]) -> Self:
        self.console.get_datetime = get_datetime
        return self

    def get_time_calleble(self, get_time: Callable[[], float]) -> Self:
        self.console.get_time = get_time
        self.console.get_time = get_time
        return self

    def environ(self, environ: Mapping[str, str]) -> Self:
        self.console._environ = environ
        return self
