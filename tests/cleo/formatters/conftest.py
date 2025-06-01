# - Project   : baloto-colombia
# - User Naem : solma
# - File Name : conftest.py
# - Dir Path  : tests/cleo/formatters
# - Created on: 2025-05-31 at 16:44:56

from __future__ import annotations

from types import MappingProxyType

import pytest

from baloto.cleo.formatters.formatter import Formatter

__all__ = ()


@pytest.fixture(scope="function", name="fformatter")
def new_formatter() -> Formatter:
    return Formatter()

@pytest.fixture(scope="module", name="mformatter")
def existing_formatter() -> Formatter:
    return Formatter()

# Generator[YieldType, SendType, ReturnType]
@pytest.fixture(scope="module")
def test_messages() -> MappingProxyType:
    return MappingProxyType(
            {
                "text-plain": "This is a message without tags",
                "text-markup":  "[green]This is a [b][yellow]message[/] without tags[/][/]",
                "text-full-markup":  "[green]This is a [bold][yellow]message[/yellow] without tags[/green][/bold]",
                "text-ansi":  "\x1b[1;38;5;76mThis is an ansi message\x1b[0m",
                "text-ansi-plain":  "This is an ansi message",
                "text-ansi-markup":  "[bold color(76)]This is an ansi message[/bold color(76)]",
                "lorem": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quisque in metus sed sapien ultricies pretium a at justo. Maecenas luctus velit et auctor maximus."
            }
    )