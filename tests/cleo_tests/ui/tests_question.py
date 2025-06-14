# Project : baloto-colombia
# File Name : tests_question.py
# Dir Path : tests/cleo/ui
# Created on: 2025–06–07 at 14:52:54.

from __future__ import annotations

import os
from collections.abc import Callable
from typing import IO
from typing import TYPE_CHECKING

import pytest
from hamcrest import assert_that
from hamcrest import contains_string
from hamcrest import equal_to
from hamcrest import none
from pydantic import ValidationError
from pytest import param

from baloto.cleo.io.stream_io import StreamIO
from baloto.cleo.ui.question import Question

if TYPE_CHECKING:
    from baloto.cleo.io.buffered_io import BufferedIO


def test_basic_question() -> None:
    prompt = "This is a question?"
    question = Question(prompt)
    assert_that(question.prompt, equal_to(prompt), reason="Validate property prompt")
    assert_that(question.default, none(), reason="Validate property default")
    assert_that(question.is_hidden, equal_to(False), reason="Validate property hidden")
    assert_that(question.max_attempts, none(), reason="Validate property max_attempts")
    # noinspection PyTypeChecker
    assert_that(
        question._error_message_template,
        equal_to('Value "{}" is invalid'),
        reason="Validate hidden property _error_message_template",
    )

    question = Question(prompt, "default value")
    assert_that(question.default, equal_to("default value"), reason="Validate property default")


@pytest.mark.parametrize(
    ("default", "hidden", "max_attempts"),
    [
        param(1, True, None, id="int-default"),
        param("def", False, 2, id="str-default"),
        param(None, False, 2, id="none-default"),
        param(None, True, 2, id="hidden"),
        param(None, True, None, id="non-attempts"),
    ],
)
def test_question_constructor(
    default: str | int | None, hidden: bool, max_attempts: int | None
) -> None:

    prompt = "This is a question?"
    question = Question(prompt, default)
    question.is_hidden = hidden
    question.max_attempts = max_attempts

    assert_that(question.default, equal_to(default), reason="Validate property default")
    assert_that(question.is_hidden, equal_to(hidden), reason="Validate property hidden")
    assert_that(
        question.max_attempts, equal_to(max_attempts), reason="Validate property max_attempts"
    )


def test_max_attempts_greater_than_zero() -> None:
    question = Question("prompt")
    with pytest.raises(ValidationError) as exc_info:
        question.max_attempts = 0

    exc = exc_info.value
    errors = exc.errors()

    from pydantic_core import ErrorDetails
    from glom import glom

    for error in errors:
        error_details: ErrorDetails = error
        assert_that(glom(error_details, "type"), equal_to("greater_than"))
        assert_that(glom(error_details, "ctx.gt"), equal_to(0))
        assert_that(glom(error_details, "msg"), contains_string("should be greater than 0"))
        assert_that(glom(error_details, "loc.0"), equal_to("max_attempts"))


def test_negative_max_attempts() -> None:
    prompt = "This is a question?"
    question = Question(prompt)
    with pytest.raises(ValidationError) as exc_info:
        question.max_attempts = -2

    assert_that(exc_info.value.error_count(), equal_to(1), reason="Expected one error only")
    assert_that(exc_info.value.title, equal_to("Question"), reason="Expected the model title")
    error = exc_info.value.errors(include_url=False, include_context=False)[0]
    assert_that(error["type"], equal_to("greater_than"), "expected contraint")
    assert_that(error["loc"][0], equal_to("max_attempts"), "expected field name")

    with pytest.raises(ValidationError) as exc_info:
        question.max_attempts = False

    error = exc_info.value.errors(include_url=False, include_context=False)[0]
    assert_that(error["msg"], contains_string("valid integer"), "expected type error")


def test_input(
    stream_io: StreamIO, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[IO[str]]
) -> None:

    def fake_input(prompt=""):
        stream_io.output._console.file.write(prompt)
        return "\n8AM\n"

    monkeypatch.setattr("builtins.input", fake_input)

    question = Question("What time is it?", "2PM")
    user_input = question.ask(stream_io)

    assert_that(
        capsys.readouterr().out,
        contains_string("What time is it?"),
        reason="stderr contains the question",
    )
    assert_that(user_input, equal_to("8AM"), "valiate fake response")


def test_hidden_response(
    stream_io: StreamIO, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[IO[str]]
) -> None:
    def fake_input(prompt, stream=None):
        stream_io.output._console.file.write(prompt)
        return "bar"

    import rich.console

    monkeypatch.setattr(rich.console, "getpass", fake_input)
    question = Question("foo:")
    question.is_hidden = True
    user_input = question.ask(stream_io)

    out = capsys.readouterr().out
    assert_that(out, equal_to("foo: "), reason="stderr contains the question")
    assert_that(user_input, equal_to("bar"), "valiate fake response")


def test_default_value(stream_io: StreamIO, monkeypatch: pytest.MonkeyPatch) -> None:
    io = stream_io

    def fake_input(prompt: str = ""):
        io.output._console.file.write(prompt)
        if text.find("white horse") > 0:
            return ""
        else:
            return "messi"

    monkeypatch.setattr("builtins.input", fake_input)

    text = "What color was the white horse of Henry IV?"
    question = Question(text, "white")
    user_input = question.ask(io)
    assert_that(
        user_input, equal_to("white"), "validate the default answer if user just presses enter"
    )

    text = "Best argentinian player?"
    question = Question(text, default="maradona")
    user_input = question.ask(io)
    assert_that(user_input, equal_to("messi"), "validate the default answer is not applied")

    text = "What color was the white horse of Henry IV?"
    question = Question(text)
    user_input = question.ask(io)
    assert_that(user_input, equal_to(""), "validate thatempty answr id not default given")


def test_no_interaction(stream_io: StreamIO) -> None:
    io = stream_io

    io.interactive(False)
    assert_that(not io.is_interactive(), reason="was set to intercative=False")

    question = Question("Do you have a job?", "not yet")
    assert_that(
        question.ask(io),
        equal_to("not yet"),
        reason="validate default value when no intercative output",
    )


def test_ask_question_with_special_characters(
    stream_io: StreamIO, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[IO[str]]
) -> None:

    def fake_input(prompt=""):
        stream_io.output._console.file.write(prompt)
        return ""

    monkeypatch.setattr("builtins.input", fake_input)
    question = Question("¿Dónde vives?", "Cañas Gordas ché")
    user_input = question.ask(stream_io)
    out = capsys.readouterr().out

    assert_that(
        user_input,
        equal_to("Cañas Gordas ché"),
        reason="special characters to be displayed in answer",
    )
    assert_that(
        out, equal_to("¿Dónde vives? "), reason="special characters to be displayed in question"
    )


def test_ask_ussing_text_buffer(buffered_io: BufferedIO) -> None:
    user_name = os.environ.get("USERNAME")
    buffered_io.set_user_input(f"{user_name}\n")
    question = Question("What is your name please?")
    user_input = question.ask(buffered_io)

    assert_that(user_input, equal_to(user_name), reason="simulated input in answer")


def test_ask_and_validate(buffered_io: BufferedIO) -> None:
    error = "This is not a color!"

    def validator(color: str) -> str:
        if color not in ["white", "black"]:
            raise ValueError(error)

        return color

    question = Question("What color was the white horse of Henry IV?", "white")
    question.set_validator(validator)
    question.max_attempts = 2

    buffered_io.set_user_input("\n")
    result = question.ask(buffered_io)
    assert_that(
        result,
        equal_to("white"),
        reason="question.ask(IO) default value returned, on first input line",
    )
    buffered_io.set_user_input("black\n")
    result = question.ask(buffered_io)
    assert_that(
        result,
        equal_to("black"),
        reason="question.ask(IO) different value on second user line",
    )

    buffered_io.set_user_input("green\nyellow\norange\n")

    with pytest.raises(ValueError) as exc_info:
        question.ask(buffered_io)

    assert_that(exc_info.value.args[0], equal_to(error), reason="validate wrong answer with exception")
