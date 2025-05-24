from __future__ import annotations

from typing import TYPE_CHECKING

from baloto.core.exceptions import ConsoleMessage
from tests.utils import print_section_rule

if TYPE_CHECKING:
    from baloto.core.cleo.io.outputs.console_output import ConsoleOutput


def stripped_property_test(console_output: ConsoleOutput) -> None:
    """Test the stripped property with various tagged inputs."""

    c = console_output.console
    c.line()

    print_section_rule(c, "Test stripping tags")
    message = ConsoleMessage("[blue underline]Hello, World!")
    console_output.write(message.stripped)
    message = ConsoleMessage("[red]Error[/]")
    console_output.write(message.stripped)
    message = ConsoleMessage("[b]Bold[/]")
    console_output.write(message.stripped)


def wrap_test(console_output: ConsoleOutput) -> None:
    """Test the wrap method with various inputs."""

    c = console_output.console
    c.line()

    print_section_rule(c, "Hello, World with blue")
    text = ConsoleMessage("Hello, World!").wrap("blue").text
    console_output.write(text)

    print_section_rule(c, "Test with error (no stderr)")
    text = ConsoleMessage("Hello, World!").wrap("error").text
    console_output.write(text)

    print_section_rule(c, "Test with empty input")
    text = ConsoleMessage("").wrap("green").text
    console_output.write(text)


def indent_test(console_output: ConsoleOutput) -> None:
    """Test the indent method with various inputs."""

    c = console_output.console
    c.line()

    print_section_rule(c, "Simple Input")
    message = ConsoleMessage("Hello, World!")
    console_output.write(message.indent("    ").text)

    print_section_rule(c, "Two Lines")
    message = ConsoleMessage("Line 1\nLine 2")
    console_output.write(message.indent(">>").text)

    print_section_rule(c, "Test with empty input")
    message = ConsoleMessage("")
    console_output.write(message.indent(" ").text)

    print_section_rule(c, "Test with whitespace input")
    message = ConsoleMessage(" ")
    console_output.write(message.indent(" ").text)


def make_section_test(console_output: ConsoleOutput) -> None:
    """Test the make_section method with various inputs."""

    c = console_output.console
    c.line()

    print_section_rule(c, "Test simple section no indent")
    message = ConsoleMessage("Hello, World!")
    actual = message.make_section("Greeting").text
    console_output.write(actual)

    print_section_rule(c, "Test simple section and section title")
    message = ConsoleMessage("This is a message.")
    actual = message.make_section("Section Title", indent=" ").text
    console_output.write(actual)

    print_section_rule(c, "Test with empty test and section title")
    message = ConsoleMessage("")
    actual = message.make_section("Title").text
    console_output.write(actual)

    print_section_rule(c, "Test with multi line and section title")
    message = ConsoleMessage("Multi-line\nText")
    actual = message.make_section("Title", indent=">>>").text
    console_output.write(actual)
