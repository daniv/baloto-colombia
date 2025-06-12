# Project : baloto-colombia
# File Name : question.py
# Dir Path : src/baloto/cleo/ui
# Created on: 2025–06–07 at 14:30:17.

from __future__ import annotations

from typing import Any
from collections.abc import Callable
from typing import TYPE_CHECKING
from typing import cast

from pydantic import BaseModel
from pydantic import Field
from pydantic import PositiveInt

from baloto.cleo.io.buffered_io import BufferedIO
from baloto.cleo.io.outputs.stream_output import StreamOutput

if TYPE_CHECKING:
    from baloto.cleo.io.io import IO


Validator = Callable[[str], Any]
Normalizer = Callable[[str], Any]

__all__ = ("Question",)


class QuestionDataModel(
    BaseModel, title="Question", validate_assignment=True, extra="ignore", strict=True
):

    question: str = Field("", min_length=2, alias="question", strict=True)
    default: Any | None = Field(None, alias="default")
    max_attempts: PositiveInt | None = Field(None, alias="maxattempts")
    is_hidden: bool = Field(False, alias="hidden")
    markup: bool = Field(True, alias="markup")


class Question:

    def __init__(self, question: str, default: Any = None) -> None:
        """A question that will be asked in a Console.

        :param question: The question text
        :param default: default value
        """
        self._question: str = question
        self._default = default

        self._max_attempts: int | None = None
        self._hidden = False
        self._markup = True
        self._validator: Validator = lambda s: s
        self._normalizer: Normalizer = lambda s: s
        self._error_message_template = 'Value "{}" is invalid'

        self._data_model = QuestionDataModel(
            question=self._question,
            default=self._default,
            is_hidden=self._hidden,
            max_attempts=self._max_attempts,
            markup=self._markup,
        )

    @property
    def prompt(self) -> str:
        return self._question

    @property
    def default(self) -> Any:
        return self._default

    @property
    def max_attempts(self) -> int | None:
        return self._max_attempts

    @max_attempts.setter
    def max_attempts(self, attempts: PositiveInt | None) -> None:
        self._data_model.max_attempts = attempts
        self._max_attempts = attempts

    @property
    def is_hidden(self) -> bool:
        return self._hidden

    @is_hidden.setter
    def is_hidden(self, hidden: bool = True) -> None:
        self._data_model.is_hidden = hidden
        self._hidden = hidden

    @property
    def markup(self) -> bool:
        return self._markup

    @markup.setter
    def markup(self, value) -> None:
        self._markup = value

    def set_validator(self, validator: Validator) -> None:
        self._validator = validator

    def ask(self, io: IO) -> Any:
        if not io.is_interactive():
            return self.default
        return self.validate_attempts(lambda: self._do_ask(io), io)

    def _do_ask(self, io: IO) -> str:

        stream = None
        if type(io) is BufferedIO:
            stream = io.input.stream
        ret = cast(StreamOutput, io.output).prompt(
            f"[miloto.question]{self._question}[/miloto.question] ",
            markup=self.markup,
            password=self.is_hidden,
            stream=stream,
        )
        if not ret:
            if len(ret) <= 0:
                if self.default is not None:
                    ret = self._default
        return self._normalizer(ret.strip())

    @staticmethod
    def write_error(io: IO, error: Exception) -> None:
        """
        Outputs an error message.
        """
        io.write_error(f"{error!s}")

    def validate_attempts(self, interviewer: Callable[[], Any], io: IO) -> Any:
        """
        Validates an attempt.
        """
        error = None
        attempts = self._max_attempts

        while attempts is None or attempts:
            if error is not None:
                self.write_error(io, error)

            try:
                return self._validator(interviewer())
            except Exception as e:
                error = e

            if attempts is not None:
                attempts -= 1

        assert error
        raise error
