from __future__ import annotations

from typing import Any, TYPE_CHECKING

from baloto.cleo.io.inputs.argument import Argument
from baloto.cleo.io.inputs.option import Option

if TYPE_CHECKING:
    from collections.abc import Sequence


def argument(
    name: str,
    description: str | None = None,
    optional: bool = False,
    multiple: bool = False,
    default: Any | None = None,
    choices: Sequence[str| None] = None
) -> Argument:
    return Argument.make(
        name,
        required=not optional,
        is_list=multiple,
        description=description,
        default=default,
            choices=choices
    )


def option(
    long_name: str,
    short_name: str | None = None,
    description: str | None = None,
    flag: bool = True,
    value_required: bool = True,
    multiple: bool = False,
    default: Any | None = None,
    choices: Sequence[str| None] = None
) -> Option:
    return Option.make(
        long_name,
        short_name,
        flag=flag,
        requires_value=value_required,
        is_list=multiple,
        description=description,
        default=default,
            choices=choices
    )


def tokenize(string: str) -> list[str]:  # pragma: no cover
    """
    Split the string using shell-like syntax. Maps directly to using `shlex.split`
    """
    import shlex

    return shlex.split(string)
