# — Project : baloto-colombia
# — File Name : test_terminal.py
# — Dir Path : tests/cleo/terminals
# — Created on: 2025-06-03 at 16:17:32.

from __future__ import annotations

import itertools
import logging
import os
import sys
from typing import TYPE_CHECKING, Generator, Callable, Any
from unittest import skipIf

import pytest
from hamcrest import assert_that, equal_to, none, is_not, any_of
from pytest import param
from rich.color import ColorSystem
from rich.console import Console, WINDOWS
from rich.pretty import Pretty
from rich.panel import Panel

if TYPE_CHECKING:
    CallableConsole = Callable[[dict[str, Any]], Console]


logger = logging.getLogger(__name__)

@pytest.fixture()
def callable_console() -> CallableConsole:

    def _console(data: dict[str, Any]) -> Console:
        if data is None:
            data = {}
        return Console(**data) # TODO: change to factory

    yield _console
    return "Console create successfuly"

'\x1b[1m[\x1b[0m\n    \x1b[3;91mfalse\x1b[0m,\n    \x1b[3;92mtrue\x1b[0m,\n    \x1b[3;35mnull\x1b[0m,\n    \x1b[32m"foo"\x1b[0m\n\x1b[1m]\x1b[0m\n'
filepath = "C:/Users/solma/PycharmProjects/baloto-colombia/tests/rich/terminals/test_terminal.py"
PRINT_TEXT = [
    "[bright_white text]A [i]text[/] [magenta]with[/] style[/]",
    f"[link={filepath}:{13}][bright_blue]click here to jump into the linked code.[/][/link]"
]

# -- ColorSystem
TRUECOLOR = ColorSystem.TRUECOLOR
WINDOWS = ColorSystem.WINDOWS
EIGHT_BIT = ColorSystem.EIGHT_BIT
STANDARD = ColorSystem.STANDARD

@pytest.mark.skipif(sys.stdout.isatty() is False, reason="requires python3.7 or higher")
@pytest.mark.parametrize("color_system", ["auto", "truecolor", "standard"])
@pytest.mark.parametrize("force_terminal", [None, True, False])
@pytest.mark.parametrize("legacy_windows", [None, True, False])
def test_console_isatty_and_non_isatty(
    record_property: Callable[[str, object], None],
    callable_console: CallableConsole, color_system: str | None, force_terminal: bool | None, legacy_windows: bool | None
):
    """
    https://gist.github.com/kurahaupo/6ce0eaefe5e730841f03cb82b061daa2

    :param callable_console: Callable of Console
    :param color_system: The color system to be tested: 'auto' (default), 'truecolor' or 'standard'
    :param force_terminal: Enable/disable terminal control codes, or None to auto-detect terminal
    :param legacy_windows:  Enable legacy Windows mode, or ``None`` to auto-detect.
    """
    record_property("Title", "ConsoleFactory on isatty and non-isatty stream")
    record_property("Description",
                    "Testing the ConsoleFactory class to validate terminal optimization on isatty stream and non-isatty stream")

    options = dict(color_system=color_system, force_terminal=force_terminal, legacy_windows=legacy_windows)
    console = callable_console(options)
    isatty = console.file.isatty()
    console.line()
    panel = Panel(Pretty(options), title=f"isatty -> {isatty}", style="yellow")
    console.print(panel, new_line_start=True)
    console.print("", *PRINT_TEXT, sep="\n")

    record_property("ISATTY MODE", isatty)

    match color_system:
        case "truecolor":
            # -- force_terminal → NONE
            if force_terminal is None and legacy_windows is None:
                assert_that(
                    console._color_system, equal_to(55),
                    reason="truecolor"
                )
                # assert_that(console._color_system, equal_to(TRUECOLOR), reason="truecolor")
                is_terminal = equal_to(True) if isatty else equal_to(False)
                assert_that(console.is_terminal, is_terminal, reason="is_terminal")
            elif force_terminal is None and legacy_windows is False:
                assert_that(console._color_system, equal_to(TRUECOLOR), reason="truecolor, not legacy")
                is_terminal = equal_to(False)
                if isatty:
                    is_terminal = equal_to(True)
                assert_that(console.is_terminal, is_terminal, reason="is_terminal")
            elif force_terminal is None and legacy_windows:
                assert_that(console._color_system, equal_to(TRUECOLOR), reason="truecolor, legacy_win")
                is_terminal = equal_to(False)
                if isatty: is_terminal = equal_to(True)
                assert_that(console.is_terminal, is_terminal, reason="is_terminal")

            # -- force_terminal → FALSE    any_of("truecolor", none())
            elif force_terminal is False and legacy_windows is None:
                assert_that(console._color_system, equal_to(TRUECOLOR), reason="truecolor, not force_term")
                assert_that(not console.is_terminal, reason="is_terminal")
            elif force_terminal is False and legacy_windows is False:
                assert_that(console._color_system, equal_to(TRUECOLOR), reason="truecolor, not force_term, not legacy_win")
                assert_that(not console.is_terminal, reason="is_terminal")
            elif force_terminal is False and legacy_windows:
                assert_that(console._color_system, equal_to(TRUECOLOR), reason="truecolor, not force_term, legacy_win")
                assert_that(not console.is_terminal, reason="is_terminal")

            # -- force_terminal → TRUE
            elif force_terminal and legacy_windows is None:
                assert_that(console.is_terminal, reason="is_terminal")
                assert_that(console._color_system, equal_to(TRUECOLOR), reason="truecolor, force_term")
            elif force_terminal and legacy_windows is False:
                assert_that(console.is_terminal, reason="is_terminal")
                assert_that(console._color_system, equal_to(TRUECOLOR), reason="truecolor|auto, force_term, not legacy")
            elif force_terminal and legacy_windows:
                assert_that(console.is_terminal, reason="is_terminal")
                assert_that(console._color_system, equal_to(TRUECOLOR), reason="truecolor, force_term, legacy_win")
            else:
                pytest.skip("Unsupported combination")

        case "standard":
            # -- force_terminal → NONE
            if force_terminal is None and legacy_windows is None:
                is_terminal = equal_to(True) if isatty else equal_to(False)
                assert_that(console.is_terminal, is_terminal, reason="is_terminal")
                assert_that(console._color_system, equal_to(STANDARD), reason="standard")
            elif force_terminal is None and legacy_windows is False:
                is_terminal = equal_to(False)
                if isatty:
                    is_terminal = equal_to(True)
                assert_that(console.is_terminal, is_terminal, reason="is_terminal")
                assert_that(console._color_system, equal_to(STANDARD), reason="standard, not legacy")
            elif force_terminal is None and legacy_windows:
                is_terminal = equal_to(False)
                if isatty:
                    is_terminal = equal_to(True)
                assert_that(console.is_terminal, is_terminal, reason="is_terminal")
                assert_that(console._color_system, equal_to(STANDARD), reason="standard, legacy_win")

            # -- force_terminal → FALSE
            elif force_terminal is False and legacy_windows is None:
                assert_that(console._color_system, equal_to(STANDARD), reason="standard, not force_term")
                assert_that(not console.is_terminal, reason="is_terminal")
            elif force_terminal is False and legacy_windows is False:
                assert_that(console._color_system, equal_to(STANDARD), reason="standard, not force_term, not legacy_win")
                assert_that(not console.is_terminal, reason="is_terminal")
            elif force_terminal is False and legacy_windows:
                assert_that(console._color_system, equal_to(STANDARD), reason="standard, not force_term, legacy_win")
                assert_that(not console.is_terminal, reason="is_terminal")

            # -- force_terminal → TRUE
            elif force_terminal and legacy_windows is None:
                assert_that(console._color_system, equal_to(STANDARD), reason="standard, force_term")
                assert_that(console.is_terminal, reason="is_terminal")
            elif force_terminal and legacy_windows is False:
                assert_that(console._color_system, equal_to(STANDARD), reason="standard, force_term, not legacy")
                assert_that(console.is_terminal, reason="is_terminal")
            elif force_terminal and legacy_windows:
                assert_that(console._color_system, equal_to(STANDARD), reason="standard, force_term, legacy_win")
                assert_that(console.is_terminal, reason="is_terminal")
            else:
                pytest.skip("Unsupported combination")

        case "auto":
            # -- force_terminal → NONE
            if force_terminal is None and legacy_windows is None:
                is_equal_none = equal_to(TRUECOLOR) if isatty else none()
                assert_that(console._color_system, is_equal_none, reason=f"auto, issaty={isatty}")
                is_terminal = equal_to(True) if isatty else equal_to(False)
                assert_that(console.is_terminal, is_terminal, reason="is_terminal")
            elif force_terminal is None and legacy_windows is False:
                color = none()
                term = equal_to(False)
                if isatty:
                    term = equal_to(True)
                    color = equal_to(TRUECOLOR)
                assert_that(console._color_system, color, reason="auto, not legacy")
                assert_that(console.is_terminal, term, reason="is_terminal")
            elif force_terminal is None and legacy_windows:
                color = none()
                term = equal_to(False)
                if isatty:
                    color = equal_to(WINDOWS)
                    term = equal_to(True)
                assert_that(console._color_system, color, reason="auto, legacy_win")
                assert_that(console.is_terminal, term, reason="is_terminal")

            # -- force_terminal → FALSE
            elif force_terminal is False and legacy_windows is None:
                assert_that(console._color_system, none(), reason="auto, not force_term")
                assert_that(not console.is_terminal, reason="is_terminal")
            elif force_terminal is False and legacy_windows is False:
                assert_that(console._color_system, none(), reason="auto, not force_term, not legacy_win")
                assert_that(not console.is_terminal, reason="is_terminal")
            elif force_terminal is False and legacy_windows:
                assert_that(console._color_system, none(), reason="auto, not force_term, legacy_win")
                assert_that(not console.is_terminal, reason="is_terminal")

            # -- force_terminal → TRUE
            elif force_terminal and legacy_windows is None:
                expected = equal_to(WINDOWS)
                # expected = equal_to(WINDOWS)
                # if isatty: expected = equal_to(TRUECOLOR)
                if isatty: expected = equal_to(TRUECOLOR)
                assert_that(console._color_system, expected, reason="auto, force_term")
                assert_that(console.is_terminal, reason="is_terminal")
            elif force_terminal and legacy_windows is False:
                is_equal = equal_to(TRUECOLOR) if isatty else equal_to(EIGHT_BIT)
                assert_that(console._color_system, is_equal, reason=f"auto, force_term, not legacy issaty={isatty}")
                assert_that(console.is_terminal, reason="is_terminal")
            elif force_terminal and legacy_windows:
                assert_that(console._color_system, equal_to(WINDOWS), reason="auto, force_term, legacy_win")
                assert_that(console.is_terminal, reason="is_terminal")
            else:
                pytest.skip("Unsupported combination")
        case _:
            pytest.skip("Not implemented system color: only ['auto', 'standard', 'truecolor']")
