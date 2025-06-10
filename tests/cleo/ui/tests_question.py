# Project : baloto-colombia
# File Name : tests_question.py
# Dir Path : tests/cleo/ui
# Created on: 2025–06–07 at 14:52:54.

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import IO
from typing import TYPE_CHECKING

import pytest
from pydantic import ValidationError
from pytest import param
from hamcrest import assert_that, equal_to, none, has_length, empty, contains_string

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
        question.autocomplete_values, has_length(0), reason="Validate property autocomplete_values"
    )
    assert_that(
        question._error_message_template,
        equal_to('Value "{}" is invalid'),
        reason="Validate hidden property _error_message_template",
    )

    assert_that(
        question._hidden_fallback,
        equal_to(False),
        reason="Validate hidden _hidden_fallback _error_message_template",
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
        param(None, True, 0, id="zero-attempts"),
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
    # noinspection PyTypeChecker
    assert_that(
        question.autocomplete_values,
        has_length(0),
        reason="Validate property autocomplete_values",
    )


def test_negative_attempts() ->None:
    prompt = "This is a question?"
    question = Question(prompt)
    with pytest.raises(ValidationError) as exc_info:
        question.max_attempts = -2

    assert_that(exc_info.value.error_count(), equal_to(1), reason="Expected one error only")
    assert_that(exc_info.value.title, equal_to("Question"), reason="Expected the model title")
    error = exc_info.value.errors(include_url=False, include_context=False)[0]
    assert_that(error['type'], equal_to("greater_than"), "expected contraint")
    assert_that(error['loc'][0], equal_to("max_attempts"), "expected field name")

    with pytest.raises(ValidationError) as exc_info:
        question.max_attempts = False

    error = exc_info.value.errors(include_url=False, include_context=False)[0]
    assert_that(error['msg'], contains_string("valid integer"), "expected type error")


def test_input(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[IO[str]]) -> None:
    def fake_input(prompt=""):
        io.write(prompt)
        return "\n8AM\n"

    io = StreamIO()
    monkeypatch.setattr("builtins.input", fake_input)

    question = Question("What time is it?", "2PM")
    user_input = question.ask(io)

    assert_that(capsys.readouterr().out, equal_to("What time is it?"), reason="stderr contains the question")
    assert_that(user_input, equal_to("bar"), "valiate fake response")

def test_hidden_response(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[IO[str]]) -> None:
    def fake_input(prompt, stream=None):
        io.output._console.file.write(prompt)
        return "bar"

    import rich.console
    monkeypatch.setattr(rich.console, "getpass", fake_input)

    io = StreamIO()
    question = Question("foo:")
    question.is_hidden = True
    user_input = question.ask(io)

    out = capsys.readouterr().out
    assert_that(out, equal_to("foo: "), reason="stderr contains the question")
    assert_that(user_input, equal_to("bar"), "valiate fake response")


def test_ask(io: BufferedIO) -> None:
    question = Question("What time is it?", "2PM")
    io.set_user_input("\n8AM\n")
    response = question.ask(io)
    assert_that(response, equal_to("2PM"), reason="Expected default value returned, buffer IO")
    io.clear_error()
    response = question.ask(io)
    assert_that(
        response, equal_to("8AM"), reason="question.ask(io) default value returned, buffer IO"
    )
    err = io.fetch_error()

    from rich.text import Text

    assert_that(
        Text.from_ansi(err).plain, equal_to("What time is it? "), "fetch_error property value"
    )


def test_ask_hidden_response(io: BufferedIO) -> None:
    question = Question("What time is it?", "2PM")
    question.hide = True
    io.set_user_input("8AM\n")

    assert question.ask(io) == "8AM"
    assert io.fetch_error() == "What time is it? "


def ask_and_validate(io: BufferedIO) -> None:
    error = "This is not a color!"

    def validator(color: str) -> str:
        if color not in ["white", "black"]:
            raise ValueError(error)

        return color

    question = Question("What color was the white horse of Henry IV?", "white")
    question.set_validator(validator)
    question.max_attempts = 2

    io.set_user_input("\nblack\n")
    assert_that(
        question.ask(io),
        equal_to("white"),
        reason="question.ask(io) default value returned, buffer IO",
    )
    assert_that(
        question.ask(io),
        equal_to("black"),
        reason="question.ask(io) default value returned, buffer IO",
    )

    io.set_user_input("green\nyellow\norange\n")

    with pytest.raises(ValueError) as e:
        question.ask(io)

    assert_that(str(e.value), equal_to(error), reason="validate wrong answer with exceprion")


def test_no_interaction(io: BufferedIO) -> None:
    io.interactive(False)
    assert_that(not io.is_interactive(), reason="was set to intercative=False")

    question = Question("Do you have a job?", "not yet")
    assert_that(
        question.ask(io),
        equal_to("not yet"),
        reason="validate default value when no intercative output",
    )


def test_ask_question_with_special_characters(io: BufferedIO) -> None:
    question = Question("What time is it, Sébastien?", "2PMë")
    io.set_user_input("\n")

    assert_that(
        question.ask(io), equal_to("2PMë"), reason="special characters to be displayed in answer"
    )
    assert_that(
        io.fetch_error(),
        equal_to("What rime is it, Sébastien? "),
        reason="special characters to be displayed in question",
    )
