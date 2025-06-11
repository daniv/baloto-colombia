from __future__ import annotations

import sys
from io import StringIO
from typing import Any
from typing import Callable
from typing import IO
from typing import Literal
from typing import Mapping
from typing import TYPE_CHECKING
from typing import TextIO

from pydantic import BaseModel
from pydantic import Field
from rich.console import Console
from rich.emoji import EmojiVariant
from rich.style import Style
from rich.text import Text



if TYPE_CHECKING:
   from baloto.core.config.settings import ConsoleConfig

ColorSystemVariant = Literal["auto", "standard", "256", "truecolor", "windows"]
HighlighterType = Callable[[str | Text], Text]
StyleType = str | Style
TextType = Text | str

FALLBACK_COLUMNS = "180"
FALLBACK_LINES = "25"


def _dict_not_none(**kwargs) -> Any:
    return {k: v for k, v in kwargs.items() if v is not None}

# class ConsoleConfig(BaseModel, arbitrary_types_allowed=True):
#     color_system: ColorSystemVariant = Field(default="truecolor")
#     force_terminal: bool = True
#     force_interactive: bool | None = None
#     soft_wrap: bool = False
#     quiet: bool = False
#     stderr: bool = False
#     width: int | None = None
#     height: int | None = None
#     style: str | None = None
#     no_color: bool | None = None
#     tab_size: int = 8
#     record: bool = False
#     markup: bool = True
#     emoji: bool = True
#     emoji_variant: EmojiVariant | None = None
#     highlight: bool = True
#     highlighter: HighlighterType | None = Field(default_factory=MilotoHighlighter)
#     legacy_windows: bool | None = None
#     safe_box: bool = True
#     environ: Mapping[str, str] | None = Field(default_factory=dict)
#     log_time: bool = True
#     log_path: bool = True


class ConsoleFactory:

    def __init__(
        self, config: ConsoleConfig, file: IO[str] | None = None
    ) -> None:
        self._config = config
        self._console: Console | None = None

        environ = config.environ
        kwargs = config.model_dump(exclude={"environ"})
        if environ:
            kwargs["_environ"] = environ

        self._console = Console(**kwargs, file=file)

    @classmethod
    def _console_config(cls) -> ConsoleConfig:
        from baloto.core.config.settings import settings
        return settings.console

    @classmethod
    def null_output(cls) -> Console:
        from rich._null_file import NullFile

        config = cls._console_config()
        config.force_interactive = False
        config.stderr = False
        config.highlight = False
        config.highlighter = None
        config.theme = None
        config.markup = False
        config.quiet = True
        config.emoji = False
        config.no_color = True

        return cls(config, file=NullFile())._console

    @classmethod
    def console_error_output(cls) -> Console:

        config = cls._console_config()
        config.force_interactive = False
        config.stderr = True
        config.quiet = False
        config.style = "red"

        return cls(config)._console

    @classmethod
    def console_output(cls) -> Console:
        config = cls._console_config()
        config.force_interactive = True
        config.stderr = False
        return cls(config)._console

    @classmethod
    def buffered_output(cls, file: TextIO[str]) -> Console:
        config = cls._console_config()
        config.force_interactive = True
        config.stderr = False
        config.stderr = False

        file = file or StringIO()
        return cls(config, file=file)._console





        # render = getattr(self.console, "_log_render")
        # self.console._log_render = ConsoleLogRender(
        #     show_time=render.time_format,
        #     show_path=render.time_format,
        #     time_format=render.time_format,
        # )