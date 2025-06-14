from __future__ import annotations

import sys
from io import StringIO

from rich.highlighter import ReprHighlighter, NullHighlighter
from rich.style import NULL_STYLE

from baloto.cleo.rich.console_factory import ConsoleFactory


# noinspection PyProtectedMember
def console_output_test() -> None:
    """
    Creates a default stdin console
    """
    console = ConsoleFactory.console_output()

    assert console._force_terminal is True
    assert console._highlight is True
    assert console.soft_wrap is True
    assert console.is_interactive is True
    assert console.is_dumb_terminal is False
    assert console.file == sys.stdout
    assert console.style is None
    assert console.quiet is False
    assert console._markup is True
    assert console.no_color is False

    assert isinstance(console.highlighter, ReprHighlighter)
    # TODO: test the theme
    # theme = ConsoleFactory.default_theme()
    # assert ConsoleFactory.default_theme().styles == console._theme_stack
    console = ConsoleFactory.console_output(soft_wrap=False)
    assert console.soft_wrap is False

# noinspection PyProtectedMember
def console_error_output_test() -> None:
    """
    Creates a default sterr console with predefined style
    """
    console = ConsoleFactory.console_error_output()

    assert console.soft_wrap is True
    assert console.style == "bold red"
    assert console.file == sys.stderr
    assert isinstance(console.highlighter, ReprHighlighter)

    console = ConsoleFactory.console_output(soft_wrap=False)
    assert console.soft_wrap is False

# noinspection PyProtectedMember
def console_null_file_test() -> None:
    console = ConsoleFactory.null_file()

    assert console._force_terminal is None
    assert console._highlight is False, "console._highlight expected to be False"
    assert console.is_interactive is False
    assert console.style is None

    from rich._null_file import NullFile
    assert isinstance(console.file, NullFile)
    assert console.quiet is False

# noinspection PyProtectedMember
def console_output_string_test() -> None:
    console = ConsoleFactory.console_output_string_io()

    assert console.soft_wrap is False, "soft_wrap expected to be False"
    assert isinstance(console.file, StringIO)

# noinspection PyProtectedMember
def console_no_color_string_io_test() -> None:
    console = ConsoleFactory.console_no_color_string_io()

    assert console._force_terminal is None
    assert isinstance(console.file, StringIO)
    assert console._highlight is False
    assert console._markup is False
    assert console.is_interactive is False
    assert isinstance(console.highlighter, NullHighlighter)
    assert console.no_color == True
    assert console.style == NULL_STYLE




