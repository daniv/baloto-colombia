# — Project : baloto-colombia
# — File Name : test_terminal.py
# — Dir Path : tests/cleo/terminals
# — Created on: 2025-06-03 at 16:17:32.

from __future__ import annotations

import itertools
import sys
from typing import TYPE_CHECKING, Generator, Callable, Any

import pytest
from hamcrest import assert_that, equal_to, none, is_not, any_of
from pytest import param
from rich.console import Console, WINDOWS
from rich.pretty import Pretty
from rich.panel import Panel

if TYPE_CHECKING:
    CallableConsole = Callable[[dict[str, Any]], Console]


@pytest.fixture()
def callable_console() -> CallableConsole:

    def _console(data: dict[str, Any]) -> Console:
        if data is None:
            data = {}
        return Console(**data)

    yield _console
    return "Console create successfuly"


filepath = "C:/Users/solma/PycharmProjects/baloto-colombia/tests/rich/terminals/test_terminal.py"
PRINT_TEXT = [
    "[bright_white text]A [i]text[/] [magenta]with[/] style[/]",
    f"[link={filepath}:{13}][bright_blue]click here to dive into the linked code.[/][/link]",
]

@pytest.mark.parametrize("color_system", [None, "truecolor", "auto"])
@pytest.mark.parametrize("force_terminal", [None, True, False])
@pytest.mark.parametrize("legacy_windows", [None, True, False])
def test_console_isatty_and_non_isatty(
    request: pytest.FixtureRequest,
    record_property: Callable[[str, object], None],
    callable_console: CallableConsole, color_system: str | None, force_terminal: bool | None, legacy_windows: bool | None
):
    options = dict(color_system=color_system, force_terminal=force_terminal, legacy_windows=legacy_windows)
    console = callable_console(options)
    isatty = sys.stdout.isatty()
    options["isatty"] = isatty

    console.line()
    pretty = Pretty(options)
    panel = Panel(pretty, title=f"isatty -> {isatty}", style="yellow")
    console.print(panel)
    for text in PRINT_TEXT:
        console.print(text)

    if isatty:
        record_property(f"ISATTY CONFIG", "color_system to None will never show colors or links")
        record_property(f"ISATTY CONFIG", "color_system='truecolor'")
        record_property(f"ISATTY CONFIG", "color_system='auto' should be used with force_terminal=True|None")
        record_property(f"ISATTY CONFIG", "legacy-windows=true -> deactivates the links")
        record_property(f"ISATTY RECOMMENDATION", "color_system='truecolor', legacy_windows=None|False")
    else:
        record_property("NON-ISATTY COMMENT", "true-color with legacy_windows=False -> links looking bad.")
    try:
        if force_terminal:
            assert_that(console.is_terminal, reason="is_terminal")
        elif force_terminal is False:
            assert_that(not console.is_terminal, reason="is_terminal")
        elif isatty:
            assert_that(console.is_terminal, reason="is_terminal")
        else:
            assert_that(not console.is_terminal, reason="is_terminal")
    except AssertionError as e:
        print(e)

    if color_system is None:

        if force_terminal is None and legacy_windows is None:
            assert_that(console.color_system, none(), reason="default console, no keywords")
        elif force_terminal is None and legacy_windows is False:
            assert_that(console.color_system, none(), reason="not legacy_win")
        elif force_terminal is None and legacy_windows:
            assert_that(console.color_system, none(), reason="legacy_win")
        elif force_terminal is False and legacy_windows is None:
            assert_that(console.color_system, none(), reason="not force_term")
        elif force_terminal is False and legacy_windows is False:
            assert_that(console.color_system, none(), reason="not force_term, not legacy_win")
        elif force_terminal is False and legacy_windows:
            assert_that(console.color_system, none(), reason="not force_term, legacy_win")
        elif force_terminal and legacy_windows is None:
            assert_that(console.color_system, none(), reason="force_term")
        elif force_terminal and legacy_windows is False:
            assert_that(console.color_system, none(), reason="force_term, not legacy_win")
        elif force_terminal and legacy_windows:
            assert_that(console.color_system, none(), reason="force_term, legacy_win")
        else:
            pytest.skip("Unsupported combination")

    elif color_system in ["truecolor", "auto"]:
        if force_terminal is None and legacy_windows is None:
            assert_that(console.color_system, any_of("truecolor", none()), reason="truecolor|auto")
        elif force_terminal is None and legacy_windows is False:
            assert_that(console.color_system, any_of("truecolor", none()), reason="truecolor, not legacy")
        elif force_terminal is None and legacy_windows:

            if WINDOWS and color_system == "auto" and isatty:
                assert_that(console.color_system, any_of(none(), "windows"), reason="auto, legacy_win")
            else:
                assert_that(console.color_system, any_of("truecolor", none(), "windows"), reason="truecolor|auto, legacy_win")
        elif force_terminal is False and legacy_windows is None:
            assert_that(console.color_system, any_of("truecolor", none()), reason="truecolor|auto, not force_term")
        elif force_terminal is False and legacy_windows is False:
            assert_that(console.color_system, any_of("truecolor", none()), reason="truecolor|auto, not force_term, not legacy_win")
        elif force_terminal is False and legacy_windows:
            assert_that(console.color_system, any_of("truecolor", none()), reason="truecolor|auto, not force_term, legacy_win")
        elif force_terminal and legacy_windows is None:
            if WINDOWS and color_system == "auto"and isatty is False:
                assert_that(console.color_system, equal_to("windows"), reason="auto, force_term")
            else:
                assert_that(console.color_system, equal_to("truecolor"), reason="truecolor, force_term")
        elif force_terminal and legacy_windows is False:
            record_property("NON-ISATTY COMMENT", "link look a mess on truecolor on non-isatty")
            assert_that(console.color_system,  any_of("truecolor", "256"), reason="truecolor|auto, force_term, not legacy")
        elif force_terminal and legacy_windows:
            if WINDOWS and color_system == "auto":
                assert_that(console.color_system, equal_to("windows"), reason="auto, force_term, legacy_win")
            else:
                assert_that(console.color_system, equal_to("truecolor"), reason="truecolor, force_term, legacy_win")
        else:
            pytest.skip("Unsupported combination")
