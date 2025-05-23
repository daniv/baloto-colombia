from __future__ import annotations

from typing import Any

import pytest

from baloto.core.cleo.exceptions import CleoLogicError
from baloto.core.cleo.exceptions import CleoValueError
from baloto.core.cleo.io.inputs.option import Option


def create_opt(
    name: str,
    shortcut: str | None = None,
    flag: bool = True,
    requires_value: bool = True,
    is_list: bool = False,
    description: str | None = None,
    default: Any | None = None,
) -> Option:
    option = Option(
        name,
        shortcut=shortcut,
        flag=flag,
        requires_value=requires_value,
        is_list=is_list,
        description=description,
        default=default,
    )

    assert option.name == name
    assert option.description == description or option.description == ""
    return option


@pytest.mark.parametrize(
    "name, matches",
    [
        ("", "An option name cannot be empty"),
        ("  ", "An option name cannot be empty"),
        ("sep word", "An option name cannot have withspace"),
    ],
    ids=["empty_name", "blank_name", "words_name"],
)
def illegal_arguments_names_test(name: str, matches: str):
    with pytest.raises(CleoValueError) as exc_info:
        Option(name)

    assert str(exc_info.value) == matches


def default_option_test() -> None:
    opt = create_opt("option")

    assert opt.name == "option"
    assert opt.description == ""
    assert opt.shortcut is None
    assert opt.is_flag()
    assert not opt.accepts_value()
    assert not opt.requires_value()
    assert not opt.is_list()
    assert not opt.default


def dashed_name_test() -> None:
    opt = Option("--option")
    assert opt.name == "option"


def fail_if_default_value_provided_for_flag_test() -> None:
    """
    Fails if default value provided for flag
    """
    with pytest.raises(CleoLogicError):
        Option("option", flag=True, default="default")


def fail_if_wrong_default_value_for_list_option_test() -> None:
    """
    Fails on wrong default value for list
    """
    with pytest.raises(CleoLogicError):
        Option("option", flag=False, is_list=True, default="default")


def option_shortcut_test() -> None:
    opt = create_opt("option", "o")
    assert opt.shortcut == "o"


def option_dashed_shortcut_test() -> None:
    opt = create_opt("option", "-o")
    assert opt.shortcut == "o"


def option_multiple_shortcuts_test() -> None:
    opt = Option("option", "-o|oo|-ooo")
    assert opt.shortcut == "o|oo|ooo"


def fail_if_shortcut_is_empty_test() -> None:
    with pytest.raises(CleoValueError):
        Option("option", "")


def option_with_optional_value_test() -> None:
    opt = create_opt("option", flag=False, requires_value=False)

    assert opt.is_flag() is False
    assert opt.accepts_value() is True
    assert opt.requires_value() is False
    assert opt.is_list() is False
    assert opt.default is None


def option_with_optional_value_with_default_test() -> None:
    opt = create_opt("option", flag=False, requires_value=False, default="Default")

    assert opt.is_flag() is False
    assert opt.accepts_value() is True
    assert opt.requires_value() is False
    assert opt.is_list() is False
    assert opt.default == "Default"


def option_with_required_value_test() -> None:
    opt = create_opt("option", flag=False, requires_value=True)

    assert opt.is_flag() is False
    assert opt.accepts_value() is True
    assert opt.requires_value() is True
    assert opt.is_list() is False
    assert opt.default is None


def option_with_list_test() -> None:
    opt = create_opt("option", flag=False, is_list=True)

    assert opt.is_flag() is False
    assert opt.accepts_value() is True
    assert opt.requires_value() is True
    assert opt.is_list() is True
    assert opt.default == []


def multi_valued_with_default_test() -> None:
    opt = create_opt("option", flag=False, is_list=True, default=["foo", "bar"])

    assert opt.is_flag() is False
    assert opt.accepts_value() is True
    assert opt.requires_value() is True
    assert opt.is_list() is True
    assert opt.default == ["foo", "bar"]
