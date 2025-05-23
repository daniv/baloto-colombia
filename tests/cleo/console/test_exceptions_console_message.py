from __future__ import annotations

import pytest
from rich import get_console

from baloto.core.exceptions import ConsoleMessage


@pytest.mark.parametrize(
    ("text", "expected_stripped"),
    [
        ("[blue underline]Hello, World!", "Hello, World!"),
        ("[red]Error[/]", "Error"),
        ("[b]Bold[/b]", "Bold"),
        ("[i]Italic[/i]", "Italic"),
    ],
    ids=["hello", "error", "bold", "italic"],
)
def stripped_property_test(text: str, expected_stripped: str) -> None:
    """Test the stripped property with various tagged inputs."""

    message = ConsoleMessage(text)
    assert message.stripped == expected_stripped


@pytest.mark.parametrize(
    ("text", "tag", "expected"),
    [
        ("Hello, World!", "blue", "[blue]Hello, World![/]"),
        ("Error occurred", "red bold", "[red bold]Error occurred[/]"),
        ("", "green", ""),  # Test with empty input
    ],
    ids=["info", "error", "empty"],
)
def wrap_test(text: str, tag: str, expected: str) -> None:
    """Test the wrap method with various inputs."""
    message = ConsoleMessage(text)
    actual = message.wrap(tag).text
    assert actual == expected
    get_console().print(actual, new_line_start=True)


@pytest.mark.parametrize(
    ("text", "indent", "expected"),
    [
        ("Hello, World!", "    ", "    Hello, World!"),
        ("Line 1\nLine 2", ">>", ">>Line 1\n>>Line 2"),
        ("", "  ", ""),  # Test with empty input
        (" ", "  ", "  "),  # Test with whitespace input
    ],
    ids=["indented", "lines", "empty", "whitespace"],
)
def indent_test(text: str, indent: str, expected: str) -> None:
    """Test the indent method with various inputs."""
    message = ConsoleMessage(text)
    actual = message.indent(indent).text
    assert actual == expected
    get_console().print(actual, new_line_start=True)


@pytest.mark.parametrize(
    ("text", "title", "indent", "expected"),
    [
        ("Hello, World!", "Greeting", "", "[b]Greeting:[/]\nHello, World!"),
        (
            "This is a message.",
            "Section Title",
            "  ",
            "[b]Section Title:[/]\n  This is a message.",
        ),
        ("", "Title", "", ""),  # Test with empty text
        ("Multi-line\nText", "Title", ">>>", "[b]Title:[/]\n>>>Multi-line\n>>>Text"),
    ],
    ids=["greeting", "lines", "indented-title", "multi-line"],
)
def make_section_test(text: str, title: str, indent: str, expected: str) -> None:
    """Test the make_section method with various inputs."""
    message = ConsoleMessage(text)
    actual = message.make_section(title, indent).text
    assert actual == expected
    get_console().print(actual, new_line_start=True)
