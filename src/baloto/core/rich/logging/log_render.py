from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Iterable
from typing import TYPE_CHECKING

from rich._log_render import LogRender
from rich.text import Text

if TYPE_CHECKING:
    from rich.console import ConsoleRenderable
    from rich.table import Table
    from rich.console import RenderableType
    from rich.console import Console
    from rich.text import TextType

    FormatTimeCallable = Callable[[datetime], Text]


__all__ = ("ConsoleLogRender",)


class ConsoleLogRender(LogRender):

    def __call__(
        self,
        console: Console,
        renderables: Iterable[ConsoleRenderable],
        log_time: datetime | None = None,
        time_format: str | FormatTimeCallable | None = None,
        level: TextType = "",
        path: str | None = None,
        line_no: int | None = None,
        link_path: str | None = None,
    ) -> Table:
        from rich.containers import Renderables
        from rich.table import Table

        output = Table.grid(padding=(0, 1))
        output.expand = True
        if self.show_time:
            output.add_column(style="log.time")
        if self.show_level:
            output.add_column(style="log.level", width=self.level_width)
        output.add_column(ratio=1, style="log.message", overflow="fold")
        if self.show_path and path:
            output.add_column(style="log.path")
        row: list[RenderableType] = []
        if self.show_time:
            log_time = log_time or console.get_datetime()
            time_format = time_format or self.time_format
            if callable(time_format):
                log_time_display = time_format(log_time)
            else:
                log_time_display = Text(log_time.strftime(time_format))
            if log_time_display == self._last_time and self.omit_repeated_times:
                row.append(Text(" " * len(log_time_display)))
            else:
                row.append(log_time_display)
                self._last_time = log_time_display
        if self.show_level:
            row.append(level)

        row.append(Renderables(renderables))

        if link_path:
            link_path = Path(link_path).as_posix()

        if self.show_path and path:
            path_text = f"[link={link_path}]{path}[/link]" if link_path else path
            if line_no:
                path_text = (
                    f"[link={link_path}:{line_no}]{path}:{line_no}[/link]"
                    if link_path
                    else f"{path}:{line_no}"
                )
            row.append(Text.from_markup(path_text, style="blue"))
        output.add_row(*row)
        return output
