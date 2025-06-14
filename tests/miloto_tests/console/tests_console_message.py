from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from pytest import param
from rich.style import Style

from baloto.miloto.console.console_message import ConsoleMessage

if TYPE_CHECKING:
    from rich.console import Console
    from rich.style import StyleType

COL_BC = "bright_cyan"
COL_BM = "bright_magenta"
COL_BW = "bright_white"
COL_BY = "bright_yellow"
COL_BR = "bright_red"

LARGE_MSG = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut "
    "labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco "
    "laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate "
    "velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, "
    "sunt in culpa qui officia deserunt mollit anim id est laborum."
)
MULTILINE_MSG = "Multi-line\nText\nline\nmore line"
INLINE_STYLE_MSG = "Text with [bold]BOLD[/] style inline"


@pytest.mark.parametrize(
    ("message", "style"),
    [
        param("Hello, World!", None, id="simple"),
        param("Hello, [green]World![/]", None, id="marked"),
        param("Hello, World!", COL_BY, id="with-style"),
        param("[yellow]Hello, [green]World![/] - Yeah![/]", None, id="marked-style"),
        param("Hello\nWorld!\nHere\ni am!", None, id="multi-line-nst"),
        param("Hello, [green]World![/] - Yeah!", "blue", id="inline-st"),
        param("Hello, World!", Style(color=COL_BM, bold=True), id="style"),
        param("Hello, World!", Style(), id="null-style"),
    ],
)
def console_message_styled_test(
    request: pytest.FixtureRequest, console_output: Console, message: str, style: StyleType | None
) -> None:
    callspec_id = request.node.callspec.id
    console_message = ConsoleMessage(message=message, style=style or "")

    expected_text = message

    match request.node.callspec.id:
        case "marked":
            expected_text = "Hello, [green]World![/green]"
        case "with-style":
            expected_text = "[bright_yellow]Hello, World![/bright_yellow]"
        case "marked-style":
            expected_text = "[yellow]Hello, [green]World![/green] - Yeah![/yellow]"
        case "inline-st":
            expected_text = "[blue]Hello, [green]World![/green] - Yeah![/blue]"
        case "style":
            expected_text = "[bold bright_magenta]Hello, World![/bold bright_magenta]"

    if request.config.option.verbose > 0:
        console_output.line()
        console_output.rule(callspec_id, characters="=", style="bold dim")
        console_output.print(console_message.text)
        console_output.rule(f"end {callspec_id}", characters="=", style="bold dim")

    assert console_message.text == expected_text, f"text property value on ({callspec_id}) failed"
    assert console_message.debug is False, f"debug property value on ({callspec_id}) failed"


@pytest.mark.parametrize(
    ("message", "expected_plain"),
    [
        ("[info]Hello, World![/info]", "Hello, World!"),
        ("[b]Bold[/b]", "Bold"),
        ("[i]Italic[/i]", "Italic"),
    ],
)
def plain_property_test(message: str, expected_plain: str) -> None:
    console_message = ConsoleMessage(message=message) # type: ignore[call-arg]
    assert console_message.plain == expected_plain


@pytest.mark.parametrize(
    ("message", "style", "indent", "ind_style"),
    [
        param("Hello, World!", None, " - ", None, id="simple"),
        param("Hello, World!", "cyan", " + ", None, id="cyan-msg"),
        param("Hello, World!", "cyan", " >>> ", "violet", id="cyan-violet"),
        param(INLINE_STYLE_MSG, None, " <<< ", None, id="inline-style"),
        param(INLINE_STYLE_MSG, "cyan", " >>> ", "yellow", id="st-inline-style"),
        param("Hello\nWorld!\nHere\ni am!", None, " >>> ", None, id="multi-line"),
        param("Hello\nWorld!", COL_BR, " ° ", None, id="style-multi-line"),
    ],
)
def console_message_indent_test(
    request: pytest.FixtureRequest,
    console_output: Console,
    message: str,
    style: StyleType | None,
    indent: str,
    ind_style: StyleType | None,
) -> None:
    callspec_id = request.node.callspec.id
    text = ConsoleMessage(message=message, style=style or "").indent(indent, style=ind_style or "").text

    expected_text = f"{indent}{message}"

    match request.node.callspec.id:
        case "marked":
            expected_text = "Hello, [green]World![/green]"
        case "cyan-msg":
            expected_text = " + [cyan]Hello, World![/cyan]"
        case "cyan-violet":
            expected_text = "[violet] >>> [cyan][/violet]Hello, World![/cyan]"
        case "inline-style":
            expected_text = " <<< Text with [bold]BOLD[/bold] style inline"
        case "st-inline-style":
            expected_text = "[yellow] >>> [cyan][/yellow]Text with [bold]BOLD[/bold] style inline[/cyan]"
        case "multi-line":
            expected_text = " >>> Hello\n >>> World!\n >>> Here\n >>> i am!"
        case "style-multi-line":
            expected_text = " ° [bright_red]Hello[/bright_red]\n ° [bright_red]World![/bright_red]"

    if request.config.option.verbose > 0:
        console_output.line()
        console_output.rule(callspec_id, characters="=", style="bold dim")
        console_output.print(text)
        console_output.rule(f"end {callspec_id}", characters="=", style="bold dim")

    assert text == expected_text, f"text property value on ({callspec_id}) failed"


def console_large_message_test(request: pytest.FixtureRequest, console_output: Console) -> None:
    text = ConsoleMessage(message=LARGE_MSG, style="bold dim").text
    plain = ConsoleMessage(message=LARGE_MSG, style="bold dim").plain

    if request.config.option.verbose > 0:
        console_output.line()
        console_output.rule("lorem ipsum", characters="=", style="bold dim")
        console_output.print(text)
        console_output.rule(f"end lorem ipsum", characters="=", style="bold dim")
    import textwrap

    text = textwrap.shorten(plain, 20, placeholder="...")
    assert text.startswith("Lorem ipsum") is True


@pytest.mark.parametrize(
    ("message", "title", "indent", "msg_style", "title_style", "indent_style"),
    [
        param("Hello, World!", "Greeting", "", None, None, None),
        param("This is a message.", "Section Title", "  ", None, None, None),
        param("Multi-line\nText", "Title", ">>>", None, None, None),
        param("Hello, World!", "Greeting", " - ", "dim", "gold3", COL_BW),
        param(MULTILINE_MSG, "Lines", " >>> ", None, None, "gold3"),
        param(MULTILINE_MSG, "Lines", " >>> ", COL_BC, None, "gold3"),
        param(MULTILINE_MSG, "Lines", " >>> ", COL_BC, COL_BY, "gold3"),
        param(MULTILINE_MSG, "Lines", " [X] ", "gold3", COL_BM, COL_BW),
        param(MULTILINE_MSG, "Lines", " * ", COL_BR, COL_BW, "gold3"),
    ],
)
def console_make_section_test(
    request: pytest.FixtureRequest,
    console_output: Console,
    message: str,
    title: str,
    indent: str,
    msg_style: StyleType | None,
    title_style: StyleType | None,
    indent_style: StyleType | None,
) -> None:
    callspec_id = request.node.callspec.id
    cm = ConsoleMessage(message=message, style=msg_style or "").make_section(
        title, title_style=title_style or "", indent=indent, indent_style=indent_style or ""
    )

    if request.config.option.verbose > 0:
        console_output.line()
        console_output.rule(callspec_id, characters="=", style="bold dim")
        console_output.print(cm.text)
        console_output.rule(f"end {callspec_id}", characters="=", style="bold dim")

        assert cm.has_section is True


def short_message_raises_validation_error_test() -> None:

    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        ConsoleMessage(message="", style="")

    with pytest.raises(ValidationError):
        ConsoleMessage(message="[bright_red][/]", style="yellow")

