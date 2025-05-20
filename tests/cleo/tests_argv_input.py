from __future__ import annotations

import sys

from typing import TYPE_CHECKING

import pytest
import allure

from baloto.core.cleo.io.inputs.argument import Argument
from baloto.core.cleo.io.inputs.argv_input import ArgvInput
from baloto.core.cleo.io.inputs.definition import Definition
from baloto.core.cleo.io.inputs.option import Option


if TYPE_CHECKING:
    from collections.abc import Iterator

@allure.title('Cleaning and restoring sys.argv')
@pytest.fixture(scope="module")
def argv() -> Iterator[None]:
    original = sys.argv[:]

    yield

    sys.argv = original

@allure.title("argv_input default value")
@allure.description("Validating the ArgvInput class no arguments default values using sys.argv")
def it_uses_argv_by_default_test(argv: Iterator[None]) -> None:
    sys.argv = ["cli.py", "foo"]

    ai = ArgvInput()

    with allure.step("Asserting attribute _tokens"):
        assert getattr(ai, "_tokens") == ["foo"]
    with allure.step("Asserting attribute script_name"):
        assert ai.script_name == "cli.py"
    with allure.step("Asserting attribute arguments"):
        assert ai.arguments == {}
    with allure.step("Asserting attribute first_argument"):
        assert ai.first_argument == "foo"