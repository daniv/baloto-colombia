from __future__ import annotations

from contextlib import nullcontext as does_not_raise
from typing import Any, TYPE_CHECKING

import pytest

from baloto.core.cleo.exceptions import CleoLogicError, CleoValueError
from baloto.core.cleo.io.inputs.argument import Argument

if TYPE_CHECKING:
    from _pytest.python_api import RaisesContext


MATCHES_STR = "A default value for a list argument must be a list"


def create_arg(
    name: str,
    required: bool = True,
    is_list: bool = False,
    description: str | None = None,
    default: Any | None = None,
) -> Argument:
    argument = Argument(
        name, required=required, is_list=is_list, description=description, default=default
    )
    assert argument.name == "foo"
    assert argument.description == description or argument.description == ""
    return argument


@pytest.mark.parametrize(
    "name, expectation",
    [
        ("", pytest.raises(CleoValueError, match="An argument name cannot be empty")),
        ("  ", pytest.raises(CleoValueError, match="An argument name cannot be empty")),
        ("sep word", pytest.raises(CleoValueError, match="An argument name cannot have withspace")),
    ],
    ids=["empty_name", "blank_name", "words_name"],
)
def bad_arguments_names_test(name: str, expectation: RaisesContext):
    """
    Creates an optional not-list argument with default str value
    """
    with expectation:
        Argument(name)


def optional_non_list_argument_test() -> None:
    """
    Creates an optional not-list argument with default str value
    """
    argument = create_arg(
        "foo", required=False, is_list=False, description="Foo description", default="bar"
    )
    assert argument.is_required() is False
    assert argument.is_list() is False
    assert argument.default == "bar"


def required_not_list_no_default_argument_test() -> None:
    """
    Creates a required not-list argument without default value
    """
    argument = create_arg("foo", is_list=False, description="Foo description")
    assert argument.is_required() is True
    assert argument.is_list() is False
    assert argument.default is None


def required_list_argument_no_desc_test() -> None:
    """
    Creates a required list argument without description and without default value
    """
    argument = create_arg("foo", is_list=True)
    assert argument.is_required() is True
    assert argument.is_list() is True
    assert argument.default == []


def required_arguments_do_not_support_default_values_test() -> None:
    """
    Creates a required argument with default value -> raises CleoLogicErro
    """
    with pytest.raises(CleoLogicError, match="Cannot set a default value for required arguments"):
        Argument("foo", description="Foo description", default="bar")


@pytest.mark.parametrize(
    "default, expectation",
    [
        ("bar", pytest.raises(CleoLogicError, match=MATCHES_STR)),
        (3, pytest.raises(CleoLogicError, match=MATCHES_STR)),
        (True, pytest.raises(CleoLogicError, match=MATCHES_STR)),
        ((4, "yes"), pytest.raises(CleoLogicError, match=MATCHES_STR)),
        ({"key": "value"}, pytest.raises(CleoLogicError, match=MATCHES_STR)),
        ({1, 2, 3}, pytest.raises(CleoLogicError, match=MATCHES_STR)),
        (["bar"], does_not_raise()),
        ([3, 4, 5], does_not_raise()),
        ([True, 1, "A", 4.8], does_not_raise()),
        ([(1, "yes"), (2, "no")], does_not_raise()),
        ([{"key1": "value1"}, {"key2": "value2"}], does_not_raise()),
        (list({1, 2, 3}), does_not_raise()),
    ],
    ids=[
        "using-str",
        "using-int",
        "using-bool",
        "using-tuple",
        "using-dict",
        "using-set",
        "using-list[str]",
        "using-list[int]",
        "using-list[Any]",
        "using-list[tuple]",
        "using-list[dict]",
        "using-list-from-set",
    ],
)
def optional_list_arguments_do_not_support_non_list_default_values_test(
    default: Any, expectation: RaisesContext
) -> None:
    """
    A default value for a list argument must be a list -> raises CleoLogicError
    """
    with expectation:
        Argument(
            "foo",
            required=False,
            is_list=True,
            description="Foo description",
            default=default,
        )
