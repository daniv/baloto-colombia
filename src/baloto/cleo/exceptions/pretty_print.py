from __future__ import annotations

from typing import TYPE_CHECKING

from rich.panel import Panel

if TYPE_CHECKING:
    from baloto.cleo.exceptions import CleoCommandError


def pretty_print_error(error: CleoCommandError) -> None:
    from rich import print as rich_print

    rich_print(pretty_error_message(error))


def pretty_error_message(error: CleoCommandError) -> Panel:
    from rich.columns import Columns

    error_col = Columns([str(error), error.command_name], column_first=True)

    return Panel.fit(
        error_col,
        title=error.title if error.title else "Baloto encountered an error.",
        title_align="left",
        border_style="red",
    )
