from __future__ import annotations

from typing import Any

import pytest
import allure

from baloto.core.cleo.exceptions import CleoLogicError
from baloto.core.cleo.exceptions import CleoValueError
from baloto.core.cleo.io.inputs.option import Option


@allure.step("Create option name={name}, requires_value={requires_value}")
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

    with allure.step("Asserting property name"):
        assert option.name == name
    with allure.step("Asserting property description"):
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
@allure.title("option with illegal names {param_id}")
@allure.description("Creates an option with illegal name")
@allure.tag("negative")
def illegal_arguments_names_test(name: str, matches: str):
    with pytest.raises(CleoValueError) as exc_info:
        Option(name)

    assert str(exc_info.value) == matches


@allure.title("Option default values")
def default_option_test() -> None:
    opt = create_opt("option")

    with allure.step("Asserting default values"):
        assert opt.name == "option"
        assert opt.description == ""
        assert opt.shortcut is None
        assert opt.is_flag()
        assert not opt.accepts_value()
        assert not opt.requires_value()
        assert not opt.is_list()
        assert not opt.default


@allure.title("Option with dashed name")
def dashed_name_test() -> None:
    opt = Option("--option")

    with allure.step("Asserting property name"):
        assert opt.name == "option"


@allure.title("Fails if default value provided for flag")
@allure.tag("negative")
def fail_if_default_value_provided_for_flag_test() -> None:
    with pytest.raises(CleoLogicError):
        Option("option", flag=True, default="default")


@allure.title("Fails on wrong default value for list")
@allure.tag("negative")
def fail_if_wrong_default_value_for_list_option_test() -> None:
    with pytest.raises(CleoLogicError):
        Option("option", flag=False, is_list=True, default="default")


@allure.title("shortcut")
def option_shortcut_test() -> None:
    opt = create_opt("option", "o")

    with allure.step("asserting shortcut property"):
        assert opt.shortcut == "o"


@allure.title("dashed shortcut")
def option_dashed_shortcut_test() -> None:
    opt = create_opt("option", "-o")

    with allure.step("asserting shortcut property"):
        assert opt.shortcut == "o"


@allure.title("multiple shortcut")
def option_multiple_shortcuts_test() -> None:
    opt = Option("option", "-o|oo|-ooo")

    with allure.step("asserting shortcut property"):
        assert opt.shortcut == "o|oo|ooo"


@allure.title("empty shortcut")
@allure.tag("negative")
def fail_if_shortcut_is_empty_test() -> None:
    with pytest.raises(CleoValueError):
        Option("option", "")


@allure.title("optional value")
def option_with_optional_value_test() -> None:
    opt = create_opt("option", flag=False, requires_value=False)

    with allure.step("asserting is_flag() method"):
        assert opt.is_flag() is False
    with allure.step("asserting accepts_value() method"):
        assert opt.accepts_value() is True
    with allure.step("asserting requires_value() method"):
        assert opt.requires_value() is False
    with allure.step("asserting is_list() method"):
        assert opt.is_list() is False
    with allure.step("asserting default property"):
        assert opt.default is None


@allure.title("optional value with default value")
def option_with_optional_value_with_default_test() -> None:
    opt = create_opt("option", flag=False, requires_value=False, default="Default")

    with allure.step("asserting is_flag() method"):
        assert opt.is_flag() is False
    with allure.step("asserting accepts_value() method"):
        assert opt.accepts_value() is True
    with allure.step("asserting requires_value() method"):
        assert opt.requires_value() is False
    with allure.step("asserting is_list() method"):
        assert opt.is_list() is False
    with allure.step("asserting default property"):
        assert opt.default == "Default"


@allure.title("required value test")
def option_with_required_value_test() -> None:
    opt = create_opt("option", flag=False, requires_value=True)

    with allure.step("asserting is_flag() method"):
        assert opt.is_flag() is False
    with allure.step("asserting accepts_value() method"):
        assert opt.accepts_value() is True
    with allure.step("asserting requires_value() method"):
        assert opt.requires_value() is True
    with allure.step("asserting is_list() method"):
        assert opt.is_list() is False
    with allure.step("asserting default property"):
        assert opt.default is None


@allure.title("option with list")
def option_with_list_test() -> None:
    opt = create_opt("option", flag=False, is_list=True)

    with allure.step("asserting is_flag() method"):
        assert opt.is_flag() is False
    with allure.step("asserting accepts_value() method"):
        assert opt.accepts_value() is True
    with allure.step("asserting requires_value() method"):
        assert opt.requires_value() is True
    with allure.step("asserting is_list() method"):
        assert opt.is_list() is True
    with allure.step("asserting default property"):
        assert opt.default == []


@allure.title("option multi with default")
def multi_valued_with_default_test() -> None:
    opt = create_opt("option", flag=False, is_list=True, default=["foo", "bar"])

    with allure.step("asserting is_flag() method"):
        assert opt.is_flag() is False
    with allure.step("asserting accepts_value() method"):
        assert opt.accepts_value() is True
    with allure.step("asserting requires_value() method"):
        assert opt.requires_value() is True
    with allure.step("asserting is_list() method"):
        assert opt.is_list() is True
    with allure.step("asserting default property"):
        assert opt.default == ["foo", "bar"]
