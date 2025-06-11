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
from hamcrest import assert_that, equal_to, none
from pytest import param
from rich.style import Style

from baloto.cleo.exceptions import ExitStatus
from baloto.cleo.exceptions.errors import CleoKeyError
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

    assert_that(ansi_color_names, equal_to(rich_names), reason="")


def test_set_style_has_style_and_style_methods(mformatter: Formatter, styled_console) -> None:

    mformatter.set_style("test", Style(color="red", bold=True))

    assert mformatter.has_style("test") is True, "The style.has_style result was not as expected"
    assert_that(
        mformatter.style("test"), equal_to("red bold"),
        reason="The style.style result was not as expected"
    )

    style_obj = Style(color="green", bold=True, underline=True)
    mformatter.set_style("as.style.obj", style_obj)
    assert mformatter.has_style("as.style.obj") is True, "The style.has_style result was not as expected"
    assert mformatter.style("as.style.obj") == style_obj, "The style.style result was not as expected"

    assert mformatter.style("as.style.obj").color.name == "green", "The style.color.name result was not as expected"


def test_create_theme(mformatter: Formatter) -> None:

    style_obj = Style(color="green", bold=True, underline=True)
    theme = mformatter.create_theme({"test": style_obj})
    style = theme.styles.get("test")
    assert style.color.name == "green", "The style.color.name result was not as expected"


def test_default_theme(mformatter: Formatter) -> None:
    default_theme = mformatter.default_theme

    assert default_theme.styles.get("alias") is not None, "The styles.get result was not as expected"
    assert default_theme.styles.get("-alias-") is None, "The styles.get result was not as expected"


@pytest.mark.parametrize("name", ["alias", "switch", "prog"])
def test_styles_names(fformatter: Formatter, name: str) -> None:
    assert name in list(fformatter.styles_names())


def test_cleo_value_error_fetching_existing_item(mformatter: Formatter) -> None:
    style = "this_style_not_exists"
    assert mformatter.has_style(style) is False

    with pytest.raises(CleoKeyError) as exc_info:
        mformatter.style(style)

    expected_msg = f'Undefined style: "this_style_not_exists"'
    assert exc_info.value.args[0] == expected_msg, "The error.msg result was not as expected"
    assert exc_info.value.exit_code == ExitStatus.USAGE_ERROR, "The exit_code result was not as expected"


def test_strip() -> None:
    from baloto.cleo.formatters.formatter import Formatter

    expected = f"prefix-Abc30000-suffix"
    marked = f"[yellow]prefix-[/][green bold]Abc30000[/][italic]-suffix[/]"
    assert_that(Formatter.strip_styles(marked), none())
    # assert Formatter.strip_styles(marked) == expected, "The strip_styles result was not as expected"


@pytest.mark.skipif(DISABLE_PRINT is True, reason=DISABLE_MSG)
def test_render_default_ansi_styles(
    mformatter: Formatter, test_messages: MappingProxyType, styled_console: Console
) -> None:
    if mformatter.text.plain == "":
        mformatter.set_text(test_messages.get("lorem"))
    lines = mformatter.render_styles({})
    styled_console.line()
    for line in lines:
        mformatter.set_from_ansi(line)
        styled_console.print(mformatter.text)


@pytest.mark.skipif(DISABLE_PRINT is True, reason=DISABLE_MSG)
def test_render_rich_default_ansi_styles(
    mformatter: Formatter, test_messages: MappingProxyType, styled_console: Console
) -> None:
    if mformatter.text.plain == "":
        mformatter.set_text(test_messages.get("lorem"))

    rich_styles = mformatter.rich_default_styles
    lines = mformatter.render_styles(rich_styles)
    styled_console.line()
    for line in lines:
        mformatter.set_from_ansi(line)
        styled_console.print(mformatter.text)


@pytest.mark.skipif(DISABLE_PRINT is True, reason=DISABLE_MSG)
def test_render_rich_color_styles(
    mformatter: Formatter, test_messages: MappingProxyType, styled_console: Console
) -> None:
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
    "style, expected_ansi",
    [
        param(None, "pytest-rich", id="none"),
        param("", "pytest-rich", id="blank"),
        param("default", "\x1b[39mpytest-rich\x1b[0m", id="default-str"),
        param("green", "\x1b[32mpytest-rich\x1b[0m", id="green-str"),
        param("blue bold", "\x1b[1;34mpytest-rich\x1b[0m", id="blue-bold-str"),
        param(Style(), "pytest-rich", id="null-style"),
        param(Style(color="default"), "\x1b[39mpytest-rich\x1b[0m", id="default-style"),
        param(Style(color="green"), "\x1b[32mpytest-rich\x1b[0m", id="green-style"),
        param(Style(color="blue", bold=True), "\x1b[1;34mpytest-rich\x1b[0m", id="blue-bold-style"),
    ],
)
def test_to_ansi(fformatter: Formatter, style: StyleType | None, expected_ansi: str) -> None:
    text = "pytest-rich"

    fformatter.set_text(text, style=style)
    ansi = fformatter.to_ansi()
    assert ansi == expected_ansi, "The formatter.to_ansi result was not as expected"


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
