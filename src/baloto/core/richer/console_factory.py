from __future__ import annotations

from collections.abc import Callable
from io import StringIO
from typing import IO
from typing import Literal
from typing import TYPE_CHECKING
from typing import TextIO

from rich.console import Console
from rich.style import Style
from rich.text import Text

from baloto.core.richer import get_rich_settings
from baloto.core.richer.stash import RichStashKey

if TYPE_CHECKING:
    pass

ColorSystemVariant = Literal["auto", "standard", "256", "truecolor", "windows"]
HighlighterType = Callable[[str | Text], Text]
StyleType = str | Style
TextType = Text | str

console_key = RichStashKey[Console]()
eror_console_key = RichStashKey[Console]()


# noinspection PyMethodParameters
class ConsoleFactory:

    def __init__(self, file: IO[str] | None = None) -> None:
        console_settings = get_rich_settings().console_settings
        environ = console_settings.environ
        config = console_settings.model_dump(
            exclude_none=True, exclude_defaults=False, exclude={"environ"}
        )
        self._console: Console | None = None
        if environ:
            config["_environ"] = environ

        self._console = Console(**config, file=file)

    # noinspection PyProtectedMember
    @classmethod
    def null_output(cls) -> Console:
        from rich._null_file import NullFile

        console_settings = get_rich_settings().console_settings
        console_settings.force_interactive = False
        console_settings.stderr = False
        console_settings.highlight = False
        console_settings.highlighter = None
        console_settings.theme = None
        console_settings.markup = False
        console_settings.quiet = True
        console_settings.emoji = False
        console_settings.no_color = True

        return cls(file=NullFile())._console

    @classmethod
    def console_error_output(cls) -> Console:
        rich_settings = get_rich_settings()
        error_console = rich_settings.stash.get(eror_console_key, None)
        if error_console is None:
            console_settings = rich_settings.console_settings
            console_settings.color_system = "truecolor"
            console_settings.force_interactive = False
            console_settings.stderr = True
            console_settings.quiet = False
            console_settings.style = "red"
            console_settings.theme = rich_settings.theme
            console_settings.highlighter = rich_settings.highlighter
            error_console = cls()._console
            rich_settings = get_rich_settings()
            rich_settings.RICH_SETTINGS.stash.setdefault(eror_console_key, error_console)

        return error_console

    @classmethod
    def console_output(cls) -> Console:
        rich_settings = get_rich_settings()
        console = rich_settings.stash.get(console_key, None)
        if console is None:
            console_settings = rich_settings.console_settings
            console_settings.color_system = "truecolor"
            console_settings.force_interactive = True
            console_settings.stderr = False
            console_settings.theme = rich_settings.theme
            console_settings.highlighter = rich_settings.highlighter
            console = cls()._console
            get_rich_settings().stash.setdefault(console_key, console)
        return console

    @classmethod
    def buffered_output(cls, file: TextIO[str]) -> Console:
        console_settings = get_rich_settings().console_settings
        console_settings.color_system = "standard"
        console_settings.force_interactive = True
        console_settings.stderr = False
        console_settings.stderr = False

        file = file or StringIO()
        return cls(file=file)._console

        # render = getattr(self.console, "_log_render")
        # self.console._log_render = ConsoleLogRender(
        #     show_time=render.time_format,
        #     show_path=render.time_format,
        #     time_format=render.time_format,
        # )
