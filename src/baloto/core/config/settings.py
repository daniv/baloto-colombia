# Project : baloto-colombia
# File Name : settings.py
# Dir Path : src/baloto/miloto/config
# Created on: 2025–06–10 at 21:44:24.

from __future__ import annotations

import logging
import shutil
import sys
from collections.abc import Callable
from datetime import datetime
from os import isatty
from types import ModuleType
from typing import Any
from typing import Literal
from typing import Mapping
from collections.abc import Sequence
from typing import TYPE_CHECKING

from pydantic import AliasChoices
from pydantic import AmqpDsn
from pydantic import BaseModel
from pydantic import Field
from pydantic import ImportString
from pydantic import PositiveInt
from pydantic import PostgresDsn
from pydantic import RedisDsn
from pydantic import StrictBool
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from rich.emoji import EmojiVariant
from rich.highlighter import Highlighter
from rich.highlighter import ReprHighlighter
from rich.style import Style
from rich.syntax import SyntaxTheme
from rich.text import Text
from rich.theme import Theme

from baloto.cleo.io.outputs.output import Verbosity

__all__ = ("BalotoSettings", "settings", "ConsoleConfig", "TracebackSettings")

from baloto.core.rich.theme import BalotoHighlighter
from baloto.core.rich.theme import BalotoSyntaxTheme

from baloto.core.rich.theme import BalotoTheme

ColorSystemVariant = Literal["auto", "standard", "256", "truecolor", "windows"]
HighlighterType = Callable[[str | Text], Text]
StyleType = str | Style
TextType = Text | str


def _isatty_link() -> bool:
    if sys.stdout.isatty():
        return True
    return False

class TracebackSettings(BaseModel):
    width: int | None = Field(None, description="Number of characters used to render tracebacks, or None for full width. Defaults to None.")
    code_width: int = Field(88, description="Number of code characters used to render tracebacks. Defaults to 88.")
    extra_lines: int = Field(3, description="Additional lines of code to render tracebacks, Defaults to 3.")
    theme: str = Field("baloto_dark", description="Override pygments theme used in traceback.")
    word_wrap: bool = Field(True, description="Enable word wrapping of long tracebacks lines. Defaults to True.")
    show_locals: bool = Field(False, description="Enable display of locals in tracebacks. Defaults to False.")
    max_frames: PositiveInt = Field(100, description="Maximum number of frames returned by traceback.")
    max_length: PositiveInt = Field(10, description="Maximum length of containers before abbreviating, Defaults to 10.")
    max_string: int = Field(80, description="Maximum length of string before truncating, Defaults to 80.", ge=20)
    enable_link_path: bool = Field(True, strict=True, description="Enable terminal link of path column to file. Defaults to True.")
    isatty_link: bool = Field(_isatty_link(), strict=True, description="Disables the link to file on issaty mode")


class LoggignSettings(BaseModel, arbitrary_types_allowed=True):
    level: int | str = Field(logging.NOTSET, description="Log level. Defaults to logging.NOTSET.")
    show_time: bool = Field(True, description="Show a column for the time. Defaults to True.")
    show_level: bool = Field(True, description="Show a column for the level. Defaults to True.")
    show_path: bool = Field(True, description="Show the path to the original log call. Defaults to True.")
    omit_repeated_times: bool = Field(True, description="Omit repetition of the same time. Defaults to True.")
    enable_link_path: StrictBool = Field(True, description="Enable terminal link of path column to file. Defaults to True.")
    markup: bool = Field(False, description="Enable console markup in log messages. Defaults to False.")
    rich_tracebacks: bool = Field(False, description="Enable rich tracebacks with syntax highlighting and formatting. Defaults to False.")
    theme: str = Field("miloto_theme", description="Override pygments theme used in traceback.")
    log_time_format: str | None = Field(False, description="If ``log_time`` is enabled, either string for strftime or callable that formats the time. Defaults to '[%X]'")
    keywords: list[str] | None = Field([], description="List of words to highlight instead of ``RichHandler.KEYWORDS``.")


class ConsoleConfig(BaseModel, arbitrary_types_allowed=True):
    color_system: ColorSystemVariant = Field(default="truecolor")
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
    highlighter: HighlighterType | None = None
    legacy_windows: bool | None = Field(None)
    safe_box: bool = True
    environ: Mapping[str, str] | None = Field(default_factory=dict)
    log_time: bool = True
    log_path: bool = True

def pydevd_mode() -> bool:
    pydevd = sys.modules.get("pydevd")
    return pydevd is not None


def debugger_mode() -> bool:
    get_trace = getattr(sys, "gettrace", None)
    return False if get_trace is None else True




class BalotoSettings(BaseSettings, case_sensitive=True):
    model_config = SettingsConfigDict(validate_default=True, env_prefix='miloto_', env_file='.env', env_file_encoding='utf-8')
    # verbose: Verbosity = Field(Verbosity.NORMAL, description="The verbosity level")

    foo: str = Field('xxx', alias='FooAlias')
    #auth_key: str = Field(validation_alias='my_auth_key')
    #api_key: str = Field(alias='my_api_key')
    syntax_theme: SyntaxTheme = Field(default_factory=BalotoSyntaxTheme)
    theme: Theme = Field(default_factory=BalotoTheme, description="Override pygments theme used in traceback.")
    highlighter: Highlighter = Field(default_factory=BalotoHighlighter,
                                     description="Highlighter to style log messages. Defaults to BalotoHighlighter.")

    redis_dsn: RedisDsn = Field(
        'redis://user:pass@localhost:6379/1',
        validation_alias=AliasChoices('service_redis_dsn', 'redis_url'),
    )
    pg_dsn: PostgresDsn = 'postgres://user:pass@localhost:5432/foobar'
    amqp_dsn: AmqpDsn = 'amqp://user:pass@localhost:5672/'

    special_function: ImportString[Callable[[Any], Any]] = 'math.cos'

    # to override domains:
    # export my_prefix_domains='["foo.com", "bar.com"]'
    domains: set[str] = set()

    # to override more_settings:
    # export my_prefix_more_settings='{"foo": "x", "apple": 1}'
    # terminal_size: int = Field(default_factory=lambda x, y: shutil.get_terminal_size(x, y))

    pydevd: bool = Field(default_factory=pydevd_mode)

    debugger_mode: bool = Field(default_factory=debugger_mode)

    tracebacks: TracebackSettings = TracebackSettings()

    logging: LoggignSettings = LoggignSettings()

    console: ConsoleConfig = ConsoleConfig()




settings = BalotoSettings()
