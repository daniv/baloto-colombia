# - Project   : baloto-colombia
# - User Naem : solma
# - File Name : conftest.py
# - Dir Path  : tests/cleo/formatters
# - Created on: 2025-05-31 at 15:38:09

# GIT ACTIONS https://stackoverflow.com/questions/72061054/only-run-black-on-changed-files
from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

import pytest
from hypothesis import given, strategies
from pytest import param
from rich.style import Style

from alphabets import ALPHABET_ASCII_LOWER_UPPERS
from conftest import DISABLE_PRINT, DISABLE_MSG

if TYPE_CHECKING:
    from baloto.cleo.formatters.formatter import Formatter
    from rich.console import Console
    from rich.style import StyleType


def test_ansi_color_names() -> None:
    from rich.color import ANSI_COLOR_NAMES
    from baloto.cleo.formatters.formatter import Formatter

    ansi_color_names = Formatter().ansi_color_names
    rich_names = list(ANSI_COLOR_NAMES.keys())

    assert ansi_color_names == rich_names


def test_set_style_has_style_and_style_methods(fformatter: Formatter) -> None:

    fformatter.set_style("test", style="red bold")

    assert fformatter.has_style("test") is True, "The style.has_style result was not as expected"
    assert fformatter.style("test") == "red bold", "The style.style result was not as expected"

    style_obj = Style(color="green", bold=True, underline=True)
    fformatter.set_style("as.style.obj", style_obj)
    assert fformatter.has_style("as.style.obj") is True, "The style.has_style result was not as expected"
    assert fformatter.style("as.style.obj") == style_obj, "The style.style result was not as expected"

    assert fformatter.style("as.style.obj").color.name == "green", "The style.color.name result was not as expected"

def test_create_theme(fformatter: Formatter) -> None:

    style_obj = Style(color="green", bold=True, underline=True)
    theme = fformatter.create_theme({"as.style.obj": style_obj})
    style = theme.styles.get("as.style.obj")
    assert style.color.name == "green", "The style.color.name result was not as expected"

def test_default_theme(fformatter: Formatter) -> None:
    default_theme = fformatter.default_theme

    assert default_theme.styles.get("alias") is not None, "The formatter.styles.get result was not as expected"
    assert default_theme.styles.get("-alias-") is None, "The formatter.styles.get result was not as expected"


@pytest.mark.parametrize("name", ["alias", "switch", "prog"])
def test_styles_names(fformatter: Formatter, name: str) -> None:
    assert "alias" in list(fformatter.styles_names())


@given(strategies.text(ALPHABET_ASCII_LOWER_UPPERS, min_size=5, max_size=10))
def test_strip(text: str) -> None:
    from baloto.cleo.formatters.formatter import Formatter

    expected = f"prefix-{text}-suffix"
    marked = f"[yellow]prefix-[/][green bold]{text}[/][italic]-suffix[/]"
    assert Formatter.strip_styles(marked) == expected, "The strip_styles result was not as expected"

@pytest.mark.skipif(DISABLE_PRINT is True, reason=DISABLE_MSG)
def test_render_default_ansi_styles(mformatter: Formatter, test_messages: MappingProxyType, styled_console: Console) -> None:
    if mformatter.text.plain == "":
        mformatter.set_text(test_messages.get("lorem"))
    lines = mformatter.render_styles({})
    styled_console.line()
    for line in lines:
        mformatter.set_from_ansi(line)
        styled_console.print(mformatter.text)

@pytest.mark.skipif(DISABLE_PRINT is True, reason=DISABLE_MSG)
def test_render_rich_default_ansi_styles(mformatter: Formatter, test_messages: MappingProxyType, styled_console: Console) -> None:
    if mformatter.text.plain == "":
        mformatter.set_text(test_messages.get("lorem"))

    rich_styles = mformatter.rich_default_styles
    lines = mformatter.render_styles(rich_styles)
    styled_console.line()
    for line in lines:
        mformatter.set_from_ansi(line)
        styled_console.print(mformatter.text)

@pytest.mark.skipif(DISABLE_PRINT is True, reason=DISABLE_MSG)
def test_render_rich_color_styles(mformatter: Formatter, test_messages: MappingProxyType, styled_console: Console) -> None:
    if mformatter.text.plain == "":
        mformatter.set_text(test_messages.get("lorem"))

    rich_colors = mformatter.rich_ansi_styles
    lines = mformatter.render_styles(rich_colors)
    styled_console.line()
    for line in lines:
        mformatter.set_from_ansi(line)
        styled_console.print(mformatter.text)

@pytest.mark.skipif(DISABLE_PRINT is True, reason=DISABLE_MSG)
def test_with_console(mformatter: Formatter, test_messages: MappingProxyType, styled_console: Console) -> None:
    if mformatter.text.plain == "":
        mformatter.set_text(test_messages.get("lorem"))

    styled_console.line()
    table = mformatter.render_rich_colors()
    styled_console.print(table)

def test_from_markup(fformatter: Formatter, test_messages: MappingProxyType) -> None:

    clean = test_messages.get("text-plain")
    full_markup = test_messages.get("text-full-markup")

    text = fformatter.set_from_markup(test_messages.get("text-markup"))

    assert text.plain == clean, "The formatter.set_from_markup.plain result was not as expected"
    assert text.markup == full_markup, "The formatter.set_from_markup.markup result was not as expected"


def test_from_ansi(fformatter: Formatter, test_messages: MappingProxyType, styled_console: Console) -> None:
    ansi_text = test_messages.get("text-ansi")
    expected_plain = test_messages.get("text-ansi-plain")
    expected_markup = test_messages.get("text-ansi-markup")

    text = fformatter.set_from_ansi(ansi_text)
    assert text.plain == expected_plain, "The formatter.set_from_markup.plain result was not as expected"
    assert text.markup == expected_markup, "The formatter.set_from_markup.plain result was not as expected"
    styled_console.line()
    styled_console.print(text)


@pytest.mark.parametrize(
        "style, expected_ansi", [
            param(None, "pytest-rich", id="none"),
            param("", "pytest-rich", id="blank"),
            param("default", "\x1b[39mpytest-rich\x1b[0m", id="default-str"),
            param("green", "\x1b[32mpytest-rich\x1b[0m", id="green-str"),
            param("blue bold", "\x1b[1;34mpytest-rich\x1b[0m", id="blue-bold-str"),
            param(Style(), "pytest-rich", id="null-style"),
            param(Style(color="default"), "\x1b[39mpytest-rich\x1b[0m", id="default-style"),
            param(Style(color="green"), "\x1b[32mpytest-rich\x1b[0m", id="green-style"),
            param(Style(color="blue", bold=True), "\x1b[1;34mpytest-rich\x1b[0m", id="blue-bold-style")
        ]
)
def test_to_ansi(fformatter: Formatter, style: StyleType | None, expected_ansi: str) -> None:
    text = "pytest-rich"

    fformatter.set_text(text, style=style)
    ansi = fformatter.to_ansi()
    assert ansi == expected_ansi, "The formatter.to_ansi result was not as expected"


@given(strategies.text(min_size=20, max_size=30))
@pytest.mark.skipif(DISABLE_PRINT is True, reason=DISABLE_MSG)
def test_higlight_words(mformatter: Formatter, test_messages: MappingProxyType, styled_console: Console, text: str):
    mformatter.set_text(text)

    mformatter.highlight_words(["Lorem"], "bold")
    mformatter.highlight_words(["ipsum"], "italic")
    #
    styled_console.rule("justify='left'")
    styled_console.print(text, style="red")
    styled_console.line()

    styled_console.rule("justify='center'")
    styled_console.print(text, style="green", justify="center")
    styled_console.line()

    styled_console.rule("justify='right'")
    styled_console.print(text, style="blue", justify="right")
    styled_console.line()

    styled_console.rule("justify='full'")
    styled_console.print(text, style="magenta", justify="full")
    styled_console.line()
