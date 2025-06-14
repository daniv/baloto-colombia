from __future__ import annotations

from collections.abc import Callable

import pytest
from baloto.utils.helpers import EMPTY_STRING, EMPTY_LIST

from baloto.cleo.exceptions import ExitStatus
from baloto.cleo.exceptions.errors import CleoLogicError
from baloto.cleo.io.inputs.option import Option

CHOICES_LIST = ["yes", "no", "maybe"]


@pytest.mark.parametrize("name", ["opt", "--opt"], ids=["option", "dashed-option"])
def test_defualt_option(name: str) -> None:

    opt = Option(name=name)

    assert opt.name == "opt", "The Option.name was not as expected"
    assert opt.requires_value is True, "The Option.requires_value was not as expected"
    assert opt.is_list is False, "The Option.is_list was not as expected"
    assert opt.is_flag is True, "The Option.is_flag was not as expected"
    assert opt.default is False, "The Option.default was not as expected"
    assert opt.shortcut is None, "The Option.shortcut was not as expected"
    assert opt.description == EMPTY_STRING, "The Option.default was not as expected"
    assert opt.has_choices is False, "The Option.has_choices was not as expected"
    assert opt.choices is None, "The Option.choices was not as expected"
    assert opt.accepts_value == False, "The Option.accepts_value was not as expected"
    assert opt.is_value_required() == False, "The Option.is_value_required() was not as expected"


def test_fail_if_wrong_default_value_for_list_option(assert_cleo_logic_error: Callable[[...], None]) -> None:
    match = "A default value for a list option must be a list."

    with pytest.raises(CleoLogicError, match=match) as exc_info:
        Option(name="option", flag=False, is_list=True, default="default")

    # noinspection PyArgumentList
    assert_cleo_logic_error(
        exc_info.value, message=match, code="opt-default-not-list-type", exit_code=ExitStatus.USAGE_ERROR, len_notes=1
    )


def test_fail_if_wrong_default_value_for_non_list_option(assert_cleo_logic_error: Callable[[...], None]) -> None:
    match = "A default value for a non-list option shoul not be a list."

    with pytest.raises(CleoLogicError, match=match) as exc_info:
        Option(name="option", flag=False, is_list=False, default=["A", "B", "C"])

    # noinspection PyArgumentList
    assert_cleo_logic_error(
        exc_info.value, message=match, code="opt-default-list-type", exit_code=ExitStatus.USAGE_ERROR, len_notes=1
    )


def test_fail_if_default_value_provided_for_flag(assert_cleo_logic_error: Callable[[...], None]) -> None:

    match = "A flag option cannot have a default value."
    with pytest.raises(CleoLogicError, match=match) as exc_info:
        Option(name="option", flag=True, default="default")

    # noinspection PyArgumentList
    assert_cleo_logic_error(
        exc_info.value, message=match, code="opt-flag-with-default", exit_code=ExitStatus.USAGE_ERROR, len_notes=1
    )


def test_fail_if_flag_and_list(assert_cleo_logic_error: Callable[[...], None]) -> None:

    match = "A flag option cannot be a list as well."

    with pytest.raises(CleoLogicError, match=match) as exc_info:
        Option(name="option", flag=True, is_list=True)

    # noinspection PyArgumentList
    assert_cleo_logic_error(exc_info.value, message=match, code="opt-flag-list-type")


@pytest.mark.parametrize(
    "shortcut", ["o", "-o", "-o|oo|-ooo"], ids=["shortcut", "dashed-shortcut", "multiple-shortcuts"]
)
def test_shorcuts(shortcut: str) -> None:

    opt = Option(name="option", shortcut=shortcut)
    assert opt.shortcut == shortcut, "The Option.shortcut was not as expected"


def test_fail_if_shortcut_is_empty() -> None:
    from glom import glom
    from pydantic import ValidationError

    match = "An option shortcut cannot be empty"
    with pytest.raises(ValidationError) as exc_info:
        Option.make("opt", shortcut=EMPTY_STRING)

    ve = exc_info.value
    errors = exc_info.value.errors(include_url=False, include_context=True, include_input=True)

    assert ve.error_count() == 1, "The error.error_count() was not as expected"
    for idx, error in enumerate(errors):
        assert glom(error, "type") == "shortcut-not-set", "The Option.type was not as expected"
        assert glom(error, "msg") == match, "The Option.msg was not as expected"
        assert glom(error, "input.shortcut") == EMPTY_STRING, "The Option.shortcut.name was not as expected"
        assert glom(error, "input.name") == "opt", "The Option.input.name was not as expected"


def test_option_with_optional_value() -> None:
    opt = Option.make("opt", flag=False, requires_value=False)

    assert opt.is_flag is False, "The Option.is_flag was not as expected"
    assert opt.requires_value is False, "The Option.requires_value was not as expected"
    assert opt.default is None, "The Option.default was not as expected"
    assert opt.is_list is False, "The Option.is_list was not as expected"
    assert opt.accepts_value == True, "The Option.accepts_value was not as expected"
    assert opt.is_value_required() == False, "The Option.is_value_required() was not as expected"


def test_option_with_optional_value_and_default() -> None:
    opt = Option.make("opt", flag=False, requires_value=False, default="DefaultValue")

    assert opt.is_flag is False, "The Option.is_flag was not as expected"
    assert opt.accepts_value == True, "The Option.accepts_value was not as expected"
    assert opt.requires_value is False, "The Option.requires_value was not as expected"
    assert opt.is_list is False, "The Option.is_list was not as expected"
    assert opt.default == "DefaultValue", "The Option.default was not as expected"
    assert opt.is_value_required() == False, "The Option.is_value_required() was not as expected"


def test_option_with_required_value() -> None:
    opt = Option.make("opt", flag=False, requires_value=True)

    assert opt.is_flag is False, "The Option.is_flag was not as expected"
    assert opt.accepts_value == True, "The Option.accepts_value was not as expected"
    assert opt.requires_value == True, "The Option.requires_value was not as expected"
    assert opt.is_value_required() == True, "The Option.is_value_required() was not as expected"
    assert opt.is_list is False, "The Option.is_list was not as expected"
    assert opt.default is None, "The Option.default was not as expected"


def test_option_with_list() -> None:
    opt = Option.make("opt", flag=False, is_list=True)

    assert opt.is_flag is False, "The Option.is_flag was not as expected"
    assert opt.accepts_value == True, "The Option.accepts_value was not as expected"
    assert opt.is_value_required() == True, "The Option.is_value_required() was not as expected"
    assert opt.requires_value == True, "The Option.requires_value was not as expected"
    assert opt.is_list is True, "The Option.is_list was not as expected"
    assert opt.default == EMPTY_LIST, "The Option.default was not as expected"


# CHOICES ============================================"


def test_choices() -> None:

    opt = Option.make(
        "foo", shortcut="f", description="Some choices", flag=False, requires_value=True, choices=CHOICES_LIST
    )

    assert opt.name == "foo", "The Option.shortcut was not as expected"
    assert opt.shortcut == "f", "The Option.shortcut was not as expected"
    assert opt.description == "Some choices", "The Option.description was not as expected"
    assert opt.is_flag is False, "The Option.is_flag was not as expected"
    assert opt.choices == CHOICES_LIST, "The Option.choices was not as expected"
    assert opt.default is None, "The Option.default was not as expected"
    assert opt.is_list is False, "The Option.default was not as expected"


@pytest.mark.xfail(reason="list with choices", run=True)
def test_is_list_and_choices() -> None:

    opt = Option.make(
        "foo",
        shortcut="f",
        description="Some choices",
        flag=False,
        requires_value=True,
        is_list=True,
        choices=CHOICES_LIST,
    )

    assert opt.name == "foo", "The Option.shortcut was not as expected"
    assert opt.shortcut == "f", "The Option.shortcut was not as expected"
    assert opt.description == "Some choices", "The Option.description was not as expected"
    assert opt.is_flag is False, "The Option.is_flag was not as expected"
    assert opt.choices == CHOICES_LIST, "The Option.choices was not as expected"
    assert opt.default is None, "The Option.default was not as expected"
    assert opt.is_list is True, "The Option.default was not as expected"


def test_fail_choices_if_value_required(assert_cleo_logic_error: Callable[[...], None]) -> None:
    match = "An option with choices requires a value."

    with pytest.raises(CleoLogicError) as exc_info:
        Option.make(
            "foo", shortcut="f", description="Some choices", flag=False, requires_value=False, choices=CHOICES_LIST
        )

    # noinspection PyArgumentList
    assert_cleo_logic_error(exc_info.value, message=match, code="opt-choices-required-value")


def test_fail_if_choices_provided_for_flag(assert_cleo_logic_error: Callable[[...], None]) -> None:
    match = "A flag option cannot have choices."

    with pytest.raises(CleoLogicError, match=match) as exc_info:
        Option.make(
            "foo", shortcut="f", description="Some choices", flag=True, requires_value=False, choices=CHOICES_LIST
        )

    # noinspection PyArgumentList
    assert_cleo_logic_error(exc_info.value, message=match, code="opt-choices-on-flag")


def test_option_default_not_in_choices(assert_cleo_logic_error: Callable[[...], None]) -> None:
    match = "A default value must be in choices."

    with pytest.raises(CleoLogicError, match=match) as exc_info:
        Option.make(
            "foo",
            shortcut="f",
            description="Some choices",
            flag=False,
            requires_value=False,
            choices=CHOICES_LIST,
            default="agree",
        )

        # noinspection PyArgumentList
        assert_cleo_logic_error(exc_info.value, message=match, code="default-not-in-choices")


def choices_no_default_value() -> None:
    choices = ["yes", "no", "maybe"]
    opt = Option.make("opt", flag=False, is_list=True, choices=choices)

    assert opt.is_list is True, "The Option.is_list was not as expected"
    assert opt.default is None, "The Option.default was not as expected"
    assert opt.default is None, "The Option.default was not as expected"


def fail_if_default_value_type_not_as_choices() -> None:
    Option(name="option", flag=False, requires_value=False, choices=["AB", "BC"])
    opt = Option.make("opt", flag=False, choices=["yes", "no", "maybe"], default=25)


# @pytest.mark.parametrize(
#     "name, matches",
#     [
#         ("", "An option name cannot be empty"),
#         ("  ", "An option name cannot be empty"),
#         ("sep word", "An option name cannot have withspace"),
#     ],
#     ids=["empty_name", "blank_name", "words_name"],
# )
# def illegal_arguments_names(name: str, matches: str):
#     with pytest.raises(CleoValueError) as exc_info:
#         Option(name)
#
#     assert str(exc_info.value) == matches
#
#
