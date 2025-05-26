from __future__ import annotations

from typing import cast

from rich.style import Style

from baloto.core.cleo.formatters.formatter import Formatter
from baloto.core.patterns.builder import Director
from baloto.core.rich.builders.console_builder import ConsoleBuilder

__all__ = ["RichDirector"]


class RichDirector(Director):

    def __init__(self) -> None:
        super().__init__()
        self.reset()

    def reset(self) -> None:
        self._builder = None

    def console_builder(self, **kwargs) -> ConsoleBuilder: # type: ignore[no-untyped-def]

        formatter = Formatter()
        formatter.set_style("switch", Style(color="green", italic=True))
        formatter.set_style("command", Style(color="magenta", bold=True))
        formatter.set_style("alias", Style(color="magenta", italic=True, bold=True))
        formatter.set_style("prog", Style(color="medium_orchid3", bold=True))
        formatter.set_style("dark_warning", Style(color="dark_goldenrod", bold=True))
        formatter.set_style("option", Style(color="bright_cyan", bold=True))
        core_theme = formatter.create_theme()
        self._builder = ConsoleBuilder(**kwargs, theme=core_theme)

        return self._builder

