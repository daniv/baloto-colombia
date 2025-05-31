from __future__ import annotations

from typing import Any, Callable

import pytest
from pydantic import ValidationError
from pytest import param

from baloto.cleo.exceptions import ExitStatus
from baloto.cleo.exceptions.errors import CleoLogicError
from baloto.cleo.io.inputs.argument import Argument
from helpers import EMPTY_STRING

FIELD_NAME_MSG = "The field 'name' cannot contain special symbols and/or white-space."


def test_defualt_argument() -> None:
    """
    Validates Argument default values
    """

    arg = Argument(name="pytest")

    assert arg.name == "pytest", "The Argument.name was not as expected"
    assert arg.required is True, "The Argument.required was not as expected"
    assert arg.is_list is False, "The Argument.is_list was not as expected"
    assert arg.default is None, "The Argument.default was not as expected"
    assert arg.description == EMPTY_STRING, "The Argument.default was not as expected"
    assert arg.has_choices is False, "The Argument.has_choices was not as expected"
    assert arg.choices is None, "The Argument.choices was not as expected"


def test_optional_non_list_argument() -> None:
    """
    Creates an optional not-list argument with default str value
    """
    arg = Argument(name="pytest", required=False, description="pyest description", default="bar")

    assert arg.required is False, "The Argument.required was not as expected"
    assert arg.is_list is False, "The Argument.is_list was not as expected"
    assert arg.default == "bar", "The Argument.default was not as expected"


def test_required_not_list_no_default_argument() -> None:
    """
    Creates a required not-list argument without default value
    """
    arg = Argument(name="pytest", is_list=False, description="Foo description")

    assert arg.required is True, "The Argument.required was not as expected"
    assert arg.is_list is False, "The Argument.is_list was not as expected"
    assert arg.default is None, "The Argument.default was not as expected"


def test_required_list_argument_no_default() -> None:
    """
    Creates a required list argument without description and without default value
    """
    arg = Argument(name="pytest", is_list=True)

    assert arg.required is True, "The Argument.required was not as expected"
    assert arg.is_list is True, "The Argument.is_list was not as expected"
    assert arg.default == [], "The Argument.default was not as expected"

def test_required_list_argument_with_default() -> None:
    """
    Creates a required list argument without description and without default value
    """
    arg = Argument(name="pytest", is_list=True, required=False, default=[1,2,3])

    assert arg.required is False, "The Argument.required was not as expected"
    assert arg.is_list is True, "The Argument.is_list was not as expected"
    assert arg.default == [1,2,3], "The Argument.default was not as expected"


def test_argument_with_choices() -> None:
    """
    Creates an optional not-list argument with default str value
    """
    arg = Argument(name="pytest", choices=["opt1", "opt2", "opt3"])

    assert arg.has_choices is True, "The Argument.has_choices was not as expected"
    assert arg.choices == ["opt1", "opt2", "opt3"], "The Argument.is_list was not as expected"


def test_argument_choices_with_default_value() -> None:
    """
    Creates an optional not-list argument with default str value
    """
    arg = Argument(name="pytest", required=False, choices=["opt1", "opt2", "opt3"], default="opt2")

    assert arg.has_choices is True, "The Argument.has_choices was not as expected"
    assert arg.choices == ["opt1", "opt2", "opt3"], "The Argument.is_list was not as expected"
    assert arg.default == "opt2", "The Argument.default was not as expected"


def test_if_default_value_set_to_required(assert_cleo_logic_error: Callable[[...], None]) -> None:
    match = "Cannot set a default value for required arguments."

    with pytest.raises(CleoLogicError, match=match) as exc_info:
        Argument(name="foo", default="bar")

    # noinspection PyArgumentList
    assert_cleo_logic_error(
        exc_info.value,
        message=match,
        code="arg-default-on-required",
        exit_code=ExitStatus.USAGE_ERROR,
        len_notes=1
    )

def test_fail_if_default_as_list_and_not_is_list(assert_cleo_logic_error: Callable[[...], None]) -> None:
    match = "A default value for a list argument must be a list."

    with pytest.raises(CleoLogicError, match=match) as exc_info:
        Argument(name="foo", is_list=True, required=False, default=33)

    # noinspection PyArgumentList
    assert_cleo_logic_error(
        exc_info.value,
        message=match,
        code="arg-default-not-list-type",
        exit_code=ExitStatus.USAGE_ERROR,
        len_notes=1
    )

@pytest.mark.parametrize(
    "input, type, msg",
    [
        param("f", "string_too_short", "String should have at least 2 characters", id="too_short"),
        param("", "string_too_short", "String should have at least 2 characters", id="too_short"),
        param("" * 10, "string_too_short", "String should have at least 2 characters", id="too_short"),
        param(None, "string_type", "Input should be a valid string", id="string_type"),
        param(33, "string_type", "Input should be a valid string", id="string_type"),
        param("aaa" * 10, "string_too_long", "String should have at most 12 characters", id="too_long"),
        param("arg name x", "string_pattern_mismatch", FIELD_NAME_MSG, id="pattern_mismatch"),
        param("arg$", "string_pattern_mismatch", FIELD_NAME_MSG, id="pattern_mismatch"),
    ],
)
def test_arguments_invalid_names(input: Any, type: str, msg: str) -> None:
    """
    StringConstraints.max_length=12 and  StringConstraints.min_length=2
    """
    with pytest.raises(ValidationError) as exc_info:
        Argument(name=input)

    ve = exc_info.value
    errors = exc_info.value.errors(include_url=False, include_context=False, include_input=True)

    assert ve.error_count() == 1, "The error.error_count() was not as expected"
    assert ve.title == "Argument", "The error.title was not as expected"
    for idx, error in enumerate(errors):
        assert error.get("type") == type, f"The error.type was not as expected"
        assert error.get("msg") == msg, f"The error.msg was not as expected"
        assert error.get("input") == input, f"The error.input was not as expected"


def test_name_converted_to_lower_case() -> None:
    """
    StringConstraints.to_lower was set to True
    """
    arg = Argument(name="ABCD")
    assert arg.name == "abcd", f"argument.name was not as expected"


def test_name_strip_whitespace() -> None:
    """
    StringConstraints.strip_whitespace was set to True
    """
    arg = Argument(name="                    arg            ")
    assert arg.name == "arg", f"argument.name was not as expected"


def test_make_classmethod() -> None:
    """
    StringConstraints.to_lower was set to True
    """
    arg = Argument.make("arg", description="an arg")
    assert arg.name == "arg", f"argument.name was not as expected"
