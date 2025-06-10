from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import pytest
from baloto.core.cleo.io.inputs.argument import Argument
from baloto.core.cleo.io.inputs.argv_input import ArgvInput
from baloto.core.cleo.io.inputs.definition import Definition
from baloto.core.cleo.io.inputs.option import Option

if TYPE_CHECKING:
    from collections.abc import Iterator


@pytest.fixture(scope="module")
def argv() -> Iterator[None]:
    original = sys.argv[:]
    yield
    sys.argv = original


def it_uses_argv_by_default_test(argv: Iterator[None]) -> None:
    """
    Validating the ArgvInput class no arguments default values using sys.argv
    """
    sys.argv = ["cli.py", "foo"]

    ai = ArgvInput()
    assert getattr(ai, "_tokens") == ["foo"]
    assert ai.script_name == "cli.py"
    assert ai.arguments == {}
    assert ai.first_argument == "foo"


def parse_arguments_test() -> None:
    """
    Validating the ArgvInput default values
    """
    ai = ArgvInput(["cli.py", "foo"])
    arg = Argument("name")
    ai.bind(Definition([arg]))

    assert ai.script_name == "cli.py"
    assert ai.arguments == {"name": "foo"}
    assert ai.first_argument == "foo"


@pytest.mark.parametrize(
    ["args", "options", "expected_options"],
    [
        (["cli.py", "--foo"], [Option("--foo")], {"foo": True}),
        (
            ["cli.py", "--foo=bar"],
            [Option("--foo", "-f", flag=False, requires_value=True)],
            {"foo": "bar"},
        ),
        (
            ["cli.py", "--foo", "bar"],
            [Option("--foo", "-f", flag=False, requires_value=True)],
            {"foo": "bar"},
        ),
        (
            ["cli.py", "--foo="],
            [Option("--foo", "-f", flag=False, requires_value=False)],
            {"foo": ""},
        ),
        (
            ["cli.py", "--foo=", "bar"],
            [Option("--foo", "-f", flag=False, requires_value=False), Argument("name")],
            {"foo": ""},
        ),
        (
            ["cli.py", "bar", "--foo="],
            [Option("--foo", "-f", flag=False, requires_value=False), Argument("name")],
            {"foo": ""},
        ),
        (
            ["cli.py", "--foo"],
            [Option("--foo", "-f", flag=False, requires_value=False)],
            {"foo": None},
        ),
        (
            ["cli.py", "-f"],
            [Option("--foo", "-f")],
            {"foo": True},
        ),
        (
            ["cli.py", "-fbar"],
            [Option("--foo", "-f", flag=False, requires_value=True)],
            {"foo": "bar"},
        ),
        (
            ["cli.py", "-f", "bar"],
            [Option("--foo", "-f", flag=False, requires_value=True)],
            {"foo": "bar"},
        ),
        (
            ["cli.py", "-f", ""],
            [Option("--foo", "-f", flag=False, requires_value=False)],
            {"foo": ""},
        ),
        (
            ["cli.py", "-f", "", "foo"],
            [Option("--foo", "-f", flag=False, requires_value=False), Argument("name")],
            {"foo": ""},
        ),
        (
            ["cli.py", "-f", "", "-b"],
            [
                Option("--foo", "-f", flag=False, requires_value=False),
                Option("--bar", "-b"),
            ],
            {"foo": "", "bar": True},
        ),
        (
            ["cli.py", "-f", "-b", "foo"],
            [
                Option("--foo", "-f", flag=False, requires_value=False),
                Option("--bar", "-b"),
                Argument("name"),
            ],
            {"foo": None, "bar": True},
        ),
        (
            ["cli.py", "-fb"],
            [
                Option("--foo", "-f"),
                Option("--bar", "-b"),
            ],
            {"foo": True, "bar": True},
        ),
        (
            ["cli.py", "-fb", "bar"],
            [
                Option("--foo", "-f"),
                Option("--bar", "-b", flag=False, requires_value=True),
            ],
            {"foo": True, "bar": "bar"},
        ),
        (
            ["cli.py", "-fbbar"],
            [
                Option("--foo", "-f", flag=False, requires_value=False),
                Option("--bar", "-b", flag=False, requires_value=False),
            ],
            {"foo": "bbar", "bar": None},
        ),
    ],
)
def parse_options_test(
    args: list[str],
    options: list[Option],
    expected_options: dict[str, str | bool | None],
) -> None:
    ia = ArgvInput(args)
    ia.bind(Definition(options))
    assert ia.options == expected_options
