from __future__ import annotations

import codecs
import sys
from enum import IntEnum
from functools import cached_property
from io import StringIO
from typing import TYPE_CHECKING, Any, IO, Callable, Literal, Mapping, cast

from multipledispatch import dispatch
from pydantic import BaseModel, ConfigDict, Field
from rich.emoji import EmojiVariant
from rich.segment import Segment
from rich.style import Style
from rich.text import Text
from rich.theme import Theme

from baloto.cleo.formatters.theme import MilotoTheme, MilotoHighlighter
from baloto.cleo.rich.logging.log import Log
from baloto.utils import is_pydevd_mode

__all__ = ("ConsoleConfig", "Verbosity", "OutputType", "Output")

if TYPE_CHECKING:
    from baloto.cleo.io.outputs.section_output import SectionOutput
    from rich.console import JustifyMethod, RenderableType, ConsoleOptions
    from rich.console import OverflowMethod
    from rich.console import Console
    from rich.align import AlignMethod


class Verbosity(IntEnum):
    QUIET = -1  # --quiet
    NORMAL = 0
    VERBOSE = 1  # -v
    VERY_VERBOSE = 2  # -vv
    DEBUG = 3  # -vvv


class OutputType(IntEnum):
    NORMAL = 1
    RAW = 2


ColorSystemVariant = Literal["auto", "standard", "256", "truecolor", "windows"]
HighlighterType = Callable[[str | Text], Text]
StyleType = str | Style
TextType = Text | str

FALLBACK_COLUMNS = "254"
FALLBACK_LINES = "14"


class ConsoleConfig(BaseModel):
    ConfigDict(arbitrary_types_allowed=True, strict=True, extra="forbid")

    color_system: ColorSystemVariant = Field(default="truecolor")
    force_terminal: bool = True
    force_interactive: bool | None = None
    soft_wrap: bool = False
    theme: Theme | None = Field(default_factory=MilotoTheme)
    quiet: bool = False
    stderr: bool = False
    width: int | None = None
    height: int | None = None
    style: str | None = None
    no_color: bool | None = None
    tab_size: int = 8
    record: bool = False
    markup: bool = True
    emoji: bool = True
    emoji_variant: EmojiVariant | None = None
    highlight: bool = True
    highlighter: HighlighterType | None = Field(default_factory=MilotoHighlighter)
    legacy_windows: bool | None = None
    safe_box: bool = True
    environ: Mapping[str, str] | None = Field(default_factory=dict)
    log_time: bool = True
    log_path: bool = True


class Output:

    dev_mode = is_pydevd_mode()

    def __init__(
        self, config: ConsoleConfig, verbosity: Verbosity = Verbosity.NORMAL, file: IO[str] | None = None
    ) -> None:
        self._config = config
        self.verbosity = verbosity
        self._console: Console | None = None

        environ = config.environ
        kwargs = config.model_dump(exclude={"environ"})
        if environ:
            kwargs["_environ"] = environ

        self._console = Console(**kwargs, file=file)
        self._log = Log(self._console)

    @property
    def config(self) -> ConsoleConfig:
        return self._config

    @property
    def is_interactive(self) -> bool:
        return self._console.is_interactive

    @property
    def is_terminal(self) -> bool:
        return self._console.is_terminal

    @property
    def log(self) -> Log:
        return self._log

    @cached_property
    def supports_utf8(self) -> bool:
        """
        :return: whether the stream supports the UTF-8 encoding.
        """
        encoding = self._console.encoding

        try:
            return codecs.lookup(encoding).name == "utf-8"
        except LookupError:
            return True

    def is_quiet(self) -> bool:
        return self.verbosity is Verbosity.QUIET

    def is_verbose(self) -> bool:
        return self.verbosity.value >= Verbosity.VERBOSE.value

    def is_very_verbose(self) -> bool:
        return self.verbosity.value >= Verbosity.VERY_VERBOSE.value

    def is_debug(self) -> bool:
        return self.verbosity is Verbosity.DEBUG

    @dispatch()
    def clear(self) -> None:
        """
        Empties the buffer or clears the screen
        """
        if isinstance(self._console.file, StringIO):
            self._console.file = StringIO()
        else:
            self._console.clear()

    @dispatch(bool)
    def clear(self, home: bool = True) -> None:

        if isinstance(self._console.file, StringIO):
            self._console.file = StringIO()
        else:
            self._console.clear(home)

    def line(self, count: int = 1, verbosity: Verbosity = Verbosity.NORMAL) -> None:
        if verbosity.value > self.verbosity:
            return
        self._console.line(count=count)
        self._console.input()

    def rule(
        self,
        title: TextType = "",
        *,
        characters: str = "=",
        style: str | Style = "rule.line",
        align: AlignMethod = "center",
        verbosity: Verbosity = Verbosity.NORMAL,
    ) -> None:
        if verbosity.value > self.verbosity:
            return
        self._console.rule(title, characters=characters, style=style, align=align)

    def render_str(
        self,
        text: str,
        *,
        style: str | Style = "",
        justify: JustifyMethod | None = None,
        overflow: OverflowMethod | None = None,
        emoji: bool | None = None,
        markup: bool | None = None,
        highlight: bool | None = None,
        highlighter: HighlighterType | None = None,
    ) -> Text:
        return self._console.render_str(
            text,
            style=style,
            justify=justify,
            overflow=overflow,
            emoji=emoji,
            markup=markup,
            highlighter=highlighter,
            highlight=highlight,
        )

    def render_lines(
        self,
        renderable: RenderableType,
        options: ConsoleOptions | None = None,
        *,
        style: Style | None = None,
        pad: bool = True,
        new_lines: bool = False,
    ) -> list[list[Segment]]:
        return self._console.render_lines(renderable, options, style=style, pad=pad, new_lines=new_lines)

    def fetch(self) -> str | None:
        """
        Empties the buffer and returns its content.
        """
        if isinstance(self._console.file, StringIO):
            string_io: StringIO = cast(StringIO, self._console.file)
            content = string_io.getvalue()
            self._console.file = StringIO()
            return content
        return None

    def write(
        self,
        *objects: Any,
        sep: str = " ",
        end: str = "\n",
        style: str | Style | None = None,
        justify: JustifyMethod | None = None,
        overflow: OverflowMethod | None = None,
        no_wrap: bool | None = None,
        markup: bool | None = None,
        highlight: bool = True,
        width: int | None = None,
        height: int | None = None,
        crop: bool = True,
        soft_wrap: bool | None = None,
        new_line_start: bool = False,
        verbosity: Verbosity = Verbosity.NORMAL,
        type: OutputType = OutputType.NORMAL,
    ) -> None:
        if verbosity.value > self.verbosity:
            return

        if type == OutputType.RAW:
            self._console.out(*objects, sep=sep, end=end, style=style, highlight=highlight)
        else:
            self._console.print(
                *objects,
                sep=sep,
                end=end,
                style=style,
                justify=justify,
                overflow=overflow,
                no_wrap=no_wrap,
                markup=markup,
                highlight=highlight,
                width=width,
                height=height,
                crop=crop,
                soft_wrap=soft_wrap,
                new_line_start=new_line_start,
            )

    def section(self) -> SectionOutput:
        pass

    @classmethod
    def _environ(cls) -> Mapping[str, str]:
        if not isatty():
            return {"COLUMNS": FALLBACK_COLUMNS, "LINES": FALLBACK_LINES}
        return {}

    @classmethod
    def _console_config(cls) -> ConsoleConfig:
        return ConsoleConfig()

    @classmethod
    def console_output(cls, verbosity: Verbosity = Verbosity.NORMAL) -> Output:

        config = cls._console_config()
        config.force_interactive = True
        config._environ = cls._environ()
        config.stderr = False

        config.legacy_windows = None
        if not isatty():
            config.legacy_windows = False

        return cls(config, verbosity)

    @classmethod
    def console_error_output(cls, verbosity: Verbosity = Verbosity.NORMAL) -> Output:

        config = cls._console_config()
        config.force_interactive = False
        config.legacy_windows = None
        config._environ = cls._environ()
        config.stderr = True
        config.quiet = False
        config.style = "red"
        config.legacy_windows = None
        if not isatty():
            config.legacy_windows = False

        return cls(config, verbosity)

    @classmethod
    def null_output(cls) -> Output:
        from rich._null_file import NullFile

        config = cls._console_config()
        config.force_interactive = False
        config.stderr = False
        config.legacy_windows = None
        config.quiet = None
        config.highlight = False
        config.highlighter = None
        config.theme = None
        config.markup = False
        config.quiet = True
        config.emoji = False
        config.no_color = True

        return cls(config, Verbosity.QUIET, file=NullFile())

    @classmethod
    def buffered_output(cls, verbosity: Verbosity = Verbosity.NORMAL) -> Output:
        config = cls._console_config()
        config.force_interactive = True
        config._environ = cls._environ()
        config.stderr = False
        config.legacy_windows = None
        config.stderr = False

        return cls(config, verbosity, file=StringIO())


# class Outputi(ABC):
#     def __init__(self, verbosity: Verbosity = Verbosity.NORMAL, formatter: Formatter | None = None) -> None:
#         from baloto.cleo.formatters.formatter import Formatter
#         self.verbosity: Verbosity = verbosity
#         self._dev_mode = is_pydevd_mode()
#         self._formatter = formatter or Formatter()
#         self._section_outputs: list[SectionOutput] = []
#
#
#     @property
#     @abstractmethod
#     def console(self) -> Console:
#         raise NotImplementedError("[c1]console[/] is an abstract method")
#
#
#
#     @property
#     def formatter(self) -> Formatter:
#         return self._formatter
#
#     @formatter.setter
#     def formatter(self, formatter: Formatter) -> None:
#         self._formatter = formatter
#         ConsoleFactory.formatter = formatter
#
#
#
#     def log(
#         self,
#         *objects: Any,
#         sep: str = " ",
#         end: str = "\n",
#         style: str | Style | None = None,
#         justify: JustifyMethod | None = None,
#         emoji: bool | None = None,
#         markup: bool | None = None,
#         highlight: bool | None = None,
#         log_locals: bool = False,
#         verbosity: Verbosity = Verbosity.NORMAL,
#         stack_offset: int = 3,
#     ) -> None:
#
#         # if not self._dev_mode:
#         #     return
#         # if verbosity.value > self.verbosity.value and self._dev_mode:
#         #     return
#         self._log(
#             *objects,
#                 sep=sep,
#                 end=end,
#                 style=style,
#                 justify=justify,
#                 markup=markup,
#                 highlight=highlight,
#                 log_locals=log_locals,
#                 emoji=emoji,
#                 stack_offset=stack_offset
#         )
#
#
#
#     # @staticmethod
#     # def strip_ansi(value: str) -> str:
#     #     from click._compat import strip_ansi
#     #
#     #     return strip_ansi(value)
#     #
#     # @staticmethod
#     # def remove_format(text: str) -> str:
#     #     # TODO: test against formatter remove style
#     #     text = re.sub(r"\033\[[^m]*m", "", text)
#     #     return text
#
#     @abstractmethod
#     def _log(
#         self,
#         *objects: Any,
#         sep: str = " ",
#         end: str = "\n",
#         style: str | Style | None = None,
#         justify: JustifyMethod | None = None,
#         emoji: bool | None = None,
#         markup: bool | None = None,
#         highlight: bool | None = None,
#         log_locals: bool = False,
#         stack_offset: int = 1,
#     ) -> None:
#         raise NotImplementedError("[c1]_log[/] is an abstract method")


def isatty() -> bool:
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
