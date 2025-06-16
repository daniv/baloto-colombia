# Project : baloto-colombia
# File Name : settings.py
# Dir Path : src/baloto/miloto/config
# Created on: 2025–06–10 at 21:44:24.

from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any
from typing import Literal
from typing import Mapping

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import ImportString
from pydantic_settings import BaseSettings
from pydantic_settings import DotEnvSettingsSource
from pydantic_settings import PydanticBaseSettingsSource
from pydantic_settings import PyprojectTomlConfigSettingsSource
from pydantic_settings import SettingsConfigDict
from rich._log_render import LogRender
from rich.emoji import EmojiVariant
from rich.style import Style
from rich.syntax import SyntaxTheme
from rich.text import Text
from rich.theme import Theme

from baloto.cleo.io.outputs.output import Verbosity
from baloto.core.richer.stash import RichStash
from baloto.core.richer.formatters.highlighter import RichHighlighter
from baloto.core.richer.formatters.theme import RichSyntaxTheme
from baloto.core.richer.formatters.theme import RichTheme

ColorSystemVariant = Literal["auto", "standard", "256", "truecolor", "windows"]
HighlighterType = Callable[[str | Text], Text]
StyleType = str | Style
TextType = Text | str


def locate(filename: str, cwd: Path | None = None) -> Path:
    rv = Path.cwd() / filename
    cwd = Path(cwd or Path.cwd())
    candidates = [cwd]
    candidates.extend(cwd.parents)

    for path in candidates:
        requested_file = path / filename

        if requested_file.is_file():
            return requested_file

    return rv


class ConsoleSettings(BaseSettings):
    model_config = SettingsConfigDict(
        title="Tracebacks Configuration Settings",
        validate_default=True,
        validate_assignment=True,
        extra="allow",
    )
    color_system: ColorSystemVariant = Field(default="auto")
    force_terminal: bool = True
    force_interactive: bool | None = None
    soft_wrap: bool = False
    quiet: bool = False
    width: int | None = None
    height: int | None = None
    style: str | None = None
    no_color: bool | None = None
    tab_size: int = Field(8, ge=4)
    record: bool = False
    markup: bool = True
    emoji: bool = True
    stderr: bool = False
    emoji_variant: EmojiVariant | None = None
    highlight: bool = True
    legacy_windows: bool | None = Field(None)
    safe_box: bool = True
    environ: Mapping[str, str] | None = Field(default_factory=dict)
    log_time: bool = False
    log_path: bool = True

    # def model_post_init(self, context: Any, /) -> None:
    #     self.theme = BalotoTheme()
    #     self.highlighter = BalotoHighlighter()


class PyprojectInfo(BaseModel):
    path: Path | None = None
    data: dict[str, Any] = Field(default_factory=dict)

    def model_post_init(self, context: Any, /) -> None:
        from pydantic_settings import BaseSettings, SettingsConfigDict, TomlConfigSettingsSource

        class Settings(BaseSettings):
            model_config = SettingsConfigDict(toml_file=locate("pyproject.toml"))

        toml = TomlConfigSettingsSource(Settings)
        self.data = toml.toml_data
        self.path = Path(toml.toml_file_path).resolve()


class TracebacksSettingsModel(BaseModel):
    model_config = ConfigDict(
        title="Tracebacks Configuration Settings",
        validate_default=True,
        validate_assignment=True,
        extra="forbid",
    )

    code_width: int = Field(
        88, description="Number of code characters used to render tracebacks.", gt=80
    )
    extra_lines: int = Field(3, description="Additional lines of code to render tracebacks.", ge=0)
    theme: str = Field(
        "ansi_dark",
        title="Tracebacks Theme",
        description="Override pygments theme used in traceback.",
        min_length=4,
    )
    word_wrap: bool = Field(True, description="Enable word wrapping of long tracebacks lines.")
    show_locals: bool = Field(False, description="Enable display of locals in tracebacks.")
    max_frames: int = Field(
        100, title="Max Frames", description="Maximum number of frames returned by traceback.", ge=1
    )
    max_length: int = Field(
        10, description="Maximum length of containers before abbreviating.", ge=1, le=20
    )
    max_string: int = Field(80, description="Maximum length of string before truncating.", ge=20)
    enable_link_path: bool = Field(
        True, strict=True, description="Enable terminal link of path column to file."
    )
    hide_dunder: bool = Field(True, description="Hide locals prefixed with double underscore.")
    hide_sunder: bool = Field(False, description="Hide locals prefixed with single underscore.")
    indent_guides: bool = Field(True, description="Enable indent guides in code and locals.")


class LoggingSettingsModel(TracebacksSettingsModel):
    model_config = ConfigDict(
        title="Tracebacks Configuration Settings",
        validate_default=True,
        validate_assignment=True,
        extra="forbid",
    )

    log_level: int | str = Field(..., description="Log level. Defaults to logging.NOTSET.")
    show_time: bool = Field(True, description="Show a column for the time. Defaults to True.")
    show_level: bool = Field(True, description="Show a column for the level. Defaults to True.")
    show_path: bool = Field(
        True, description="Show the path to the original log call. Defaults to True."
    )
    omit_repeated_times: bool = Field(
        True, description="Omit repetition of the same time. Defaults to True."
    )
    markup: bool = Field(
        False, description="Enable console markup in log messages. Defaults to False."
    )
    rich_tracebacks: bool = Field(
        False,
        description="Enable rich tracebacks with syntax highlighting and formatting. Defaults to False.",
    )
    log_time_format: str | None = Field(
        "[%X]",
        description="If ``log_time`` is enabled, a string for strftime or callable that formats the time. Defaults to '[%X]'",
    )
    log_format: str | None = Field("%(message)s", description="The logging.formatter template")
    keywords: list[str] | None = Field(
        [], description="List of words to highlight instead of ``RichHandler.KEYWORDS``."
    )


def is_get_trace() -> bool:
    return False if getattr(sys, "gettrace", None) is None else True


class RichSettings(BaseSettings):
    model_config = SettingsConfigDict(
        title="Project Configuration Settings",
        validate_default=True,
        env_file=".env",
        pyproject_toml_depth=10,
        pyproject_toml_table_header=("tool", "rich-settings"),
        env_file_encoding="utf-8",
        extra="forbid",
        env_ignore_empty=True,
        validate_assignment=True,
        validation_error_cause=True,
        case_sensitive=False,
        use_enum_values=False,
    )

    tracebacks: TracebacksSettingsModel = Field(
        description="The rich tracebacks settings",
    )
    logging: LoggingSettingsModel = Field(
        description="The rich logging settings",
    )

    isatty_link: bool = Field(
        sys.stdout.isatty(),
        strict=True,
        description="Disables the link to file on issaty mode",
        exclude=True,
    )

    debugging_mode: bool = Field(is_get_trace())

    console_settings: ConsoleSettings = Field(default_factory=ConsoleSettings)

    syntax_theme: SyntaxTheme | None = Field(
        default_factory=RichSyntaxTheme, description="A base class for synax theme"
    )

    theme: Theme | None = Field(
        default_factory=RichTheme,
        title="Rich Theme",
        description="Override pygments theme used in traceback.",
    )

    highlighter: HighlighterType | None = Field(
        default_factory=RichHighlighter, description="An instance of a rich Highlighter"
    )

    log_render: LogRender | None = None

    special_function: ImportString[Callable[[Any], Any]] = "math.cos"

    domains: set[str] = set()

    verbosity: Verbosity = Field(Verbosity.NORMAL)

    stash: RichStash = Field(RichStash(), description="The rich stash")

    pyproject: PyprojectInfo = Field(default_factory=PyprojectInfo)

    # force_verbosity_normal: bool

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: DotEnvSettingsSource(
            BaseSettings,
            env_file=[locate("rich.env")],
            env_file_encoding="utf8",
            case_sensitive=False,
        ),
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (PyprojectTomlConfigSettingsSource(settings_cls),)


_RICH_SETTINGS: RichSettings | None = None


def get_rich_settings() -> RichSettings:
    global _RICH_SETTINGS
    if _RICH_SETTINGS is not None:
        return _RICH_SETTINGS

    _RICH_SETTINGS = RichSettings()
    return _RICH_SETTINGS
