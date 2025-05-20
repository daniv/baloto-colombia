from __future__ import annotations

from contextlib import nullcontext as does_not_raise
from typing import Any, TYPE_CHECKING

import allure
import pytest

from baloto.core.cleo.exceptions import CleoLogicError, CleoValueError
from baloto.core.cleo.io.inputs.argument import Argument

if TYPE_CHECKING:
    from _pytest.python_api import RaisesContext


@allure.step("Create argument name={name}, required={required}, is_list={is_list}")
def create_arg(
    name: str,
    required: bool = True,
    is_list: bool = False,
    description: str | None = None,
    default: Any | None = None,
) -> Argument:
    argument = Argument(
        name,
        required=required,
        is_list=is_list,
        description=description,
        default=default,
    )

    with allure.step("Asserting property name"):
        assert argument.name == "foo"
    with allure.step("Asserting property description"):
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
@allure.title("optional argument not list {param_id}")
@allure.description("Creates an optional not-list argument with default str value")
@allure.tag("negative")
def bad_arguments_names_test(name: str, expectation: RaisesContext):
    allure.dynamic.parameter("expectation", str(expectation.expected_exception))
    allure.dynamic.parameter("matching", expectation.match_expr)
    with expectation:
        Argument(name)


@allure.title("optional argument not list")
@allure.description("Creates an optional not-list argument with default str value")
def optional_non_list_argument_test() -> None:
    argument = create_arg(
        "foo", required=False, is_list=False, description="Foo description", default="bar"
    )

    with allure.step("Asserting method is_required"):
        assert argument.is_required() is False

    with allure.step("Asserting method is_list"):
        assert argument.is_list() is False

    with allure.step("Asserting property default"):
        assert argument.default == "bar"


@allure.title("required argument not list without default")
@allure.description("Creates a required not-list argument without default value")
def required_not_list_no_default_argument_test() -> None:
    argument = create_arg("foo", is_list=False, description="Foo description")

    with allure.step("Asserting method is_required"):
        assert argument.is_required() is True

    with allure.step("Asserting method is_list"):
        assert argument.is_list() is False

    with allure.step("Asserting property default"):
        assert argument.default is None


@allure.title("required argument list no desc without default value")
@allure.description(
    "Creates a required list argument without description and without default value"
)
def required_list_argument_no_desc_test() -> None:
    argument = create_arg("foo", is_list=True)

    with allure.step("Asserting method is_required"):
        assert argument.is_required() is True

    with allure.step("Asserting method is_list"):
        assert argument.is_list() is True

    with allure.step("Asserting property default value"):
        assert argument.default == []


@allure.title("required argument not support default value")
@allure.description("Creates a required argument with default value -> raises CleoLogicErro")
@allure.tag("negative")
def required_arguments_do_not_support_default_values_test() -> None:
    with pytest.raises(CleoLogicError, match="Cannot set a default value for required arguments"):
        Argument("foo", description="Foo description", default="bar")


match_str = "A default value for a list argument must be a list"


@pytest.mark.parametrize(
    "default, expectation",
    [
        ("bar", pytest.raises(CleoLogicError, match=match_str)),
        (3, pytest.raises(CleoLogicError, match=match_str)),
        (True, pytest.raises(CleoLogicError, match=match_str)),
        ((4, "yes"), pytest.raises(CleoLogicError, match=match_str)),
        ({"key": "value"}, pytest.raises(CleoLogicError, match=match_str)),
        ({1, 2, 3}, pytest.raises(CleoLogicError, match=match_str)),
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
@allure.title("optional list argument not support non-list default values {param_id}")
@allure.description("A default value for a list argument must be a list -> raises CleoLogicError")
@allure.tag("negative")
def optional_list_arguments_do_not_support_non_list_default_values_test(
    default: Any, expectation: RaisesContext
) -> None:
    allure.dynamic.parameter("default", default)
    from contextlib import nullcontext

    if not isinstance(expectation, nullcontext):
        allure.dynamic.parameter("expectation", str(expectation.expected_exception))
        allure.dynamic.parameter("matching", expectation.match_expr)
    else:
        allure.dynamic.parameter("expectation", "nullcontext")
    with expectation:
        Argument(
            "foo",
            required=False,
            is_list=True,
            description="Foo description",
            default=default,
        )
