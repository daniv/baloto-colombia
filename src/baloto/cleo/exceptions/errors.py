from __future__ import annotations


__all__ = (
    "CleoError",
    "CleoLogicError",
    "CleoRuntimeError",
    "CleoValueError",
    "CleoNoSuchOptionError",
    "CleoUserError",
    "CleoCommandNotFoundError",
    "CleoNamespaceNotFoundError",
    "CleoKeyError"
)

from typing import Any

from pydantic import validate_call

from baloto.cleo.exceptions import CleoErrorMixin, ExitStatus
from baloto.cleo.io.inputs.base_model import CALL_CONFIG
from baloto.cleo.utils import find_similar_names


class CleoError(Exception):
    """
    Base Cleo exception.
    """

    exit_code: int | None = None


class _Trimmable(CleoError):
    """Cleo can trim these tracebacks even if they're raised internally."""

class CleoNameError(CleoError, NameError):
    ...


class CleoLogicError(CleoErrorMixin, CleoError):
    """
    Raised when there is error in command arguments and/or options configuration logic.

    Usage:
    >>> raise CleoLogicError("An Error message", code='validator-argument-default-value')
    """

    exit_code: int | None = ExitStatus.USAGE_ERROR

    @validate_call(config=CALL_CONFIG)
    def __init__(self, msg: str, *, code: str | None) -> None:
        """
        :param msg: The message to prive to the exception
        :param code: the code from baloto.cleo.exceptions.CleoErrorCodes
        """
        super().__init__(msg, code=code)
        self.add_note(self._note)

    @property
    def _note(self) -> str:
        """
        :return: a string representing the causes of this exception
        """
        return "Raised when there is error in command arguments and/or options configuration logic."


class CleoRuntimeError(CleoError, RuntimeError):
    """
    Raised when wrong value was given to Cleo components.
    """

    exit_code: int | None = ExitStatus.INTERNAL_ERROR

    def __init__(self, msg: str) -> None:
        """
        :param msg: The message to prive to the exception
        """
        super().__init__(msg)

        self.add_note(self._note)

    @property
    def _note(self) -> str:
        """
        :return: a string representing the causes of this exception
        """
        return "Raised when wrong value was given to Cleo components."


class CleoNoSuchOptionError(CleoErrorMixin, CleoNameError):
    """
    Raised when command does not have given option.
    """

    exit_code: int | None = ExitStatus.USAGE_ERROR

    def __init__(self, msg: str) -> None:
        """
        :param msg: The message to prive to the exception
        """
        super().__init__(msg)

        self.add_note(self._note)

    @property
    def _note(self) -> str:
        """
        :return: a string representing the causes of this exception
        """
        return "Raised when command does not have given option."


class CleoKeyError(CleoError, KeyError):
    """
    Raised when wrong key is fetching non-existing keys
    """

    exit_code: int | None = ExitStatus.USAGE_ERROR

    def __init__(self, msg: str) -> None:
        super().__init__(msg)
        self.add_note("Raised when wrong key is fetching non-existing keys.")



class CleoValueError(CleoError, ValueError):
    """
    Raised when wrong value was given to Cleo components.
    """

    exit_code: int | None = ExitStatus.USAGE_ERROR

    def __init__(self, msg: str) -> None:
        super().__init__(msg)
        self.add_note("Raised when wrong value was given to Cleo components.")

    # def __init__(self, error_type: LiteralString, message: LiteralString, context: dict[str, Any] | None = None):
    #     from pydantic_core import PydanticCustomError
    #     self.pydantic_custom: PydanticCustomError
    #
    #     super().__init__(message)
    #     self.add_note("Raised when wrong value was given to Cleo components.")
    #     self.pydantic_custom = PydanticCustomError(error_type, message, {"error": self})


def note_deprecation(
    message: str, *, since: str, has_codemod: bool, stacklevel: int = 0
) -> None:
    if since != "RELEASEDAY":
        date = datetime.date.fromisoformat(since)
        assert datetime.date(2021, 1, 1) <= date
    if has_codemod:
        message += (
            "\n    The `hypothesis codemod` command-line tool can automatically "
            "refactor your code to fix this warning."
        )
    warnings.warn(HypothesisDeprecationWarning(message), stacklevel=2 + stacklevel)

def __getattr__(name: str) -> Any:
    if name == "MultipleFailures":
        from hypothesis._settings import note_deprecation
        from hypothesis.internal.compat import BaseExceptionGroup

        note_deprecation(
            "MultipleFailures is deprecated; use the builtin `BaseExceptionGroup` type "
            "instead, or `exceptiongroup.BaseExceptionGroup` before Python 3.11",
            since="2022-08-02",
            has_codemod=False,  # This would be a great PR though!
            stacklevel=1,
        )
        return BaseExceptionGroup

    raise AttributeError(f"Module 'hypothesis.errors' has no attribute {name}")


class CleoUserError(CleoErrorMixin, CleoError):
    """
    Base exception for user errors.
    """

    def __init__(self, msg: str, code: str | None = None) -> None:
        super().__init__(msg, code)
        self.add_note("Base exception for user errors.")


class CleoMissingArgumentsError(CleoUserError):
    """
    Raised when called command was not given required arguments.
    """

    def __init__(self, msg: str) -> None:
        super().__init__(msg, "arg-missing")
        self.add_note("Raised when called command was not given required arguments.")


class CleoCommandNotFoundError(CleoUserError):
    """
    Raised when called command does not exist.
    """

    def __init__(self, name: str, commands: list[str] | None = None) -> None:
        message = f'The command "{name}" does not exist.'
        if commands:
            suggestions = _suggest_similar_names(name, commands)
            if suggestions:
                message += "\n\n" + suggestions
        super().__init__(message, code="cmd-not-found")

        self.add_note("Raised when called command does not exist")


class CleoNamespaceNotFoundError(CleoUserError):
    """
    Raised when called namespace has no commands.
    """

    def __init__(self, name: str, namespaces: list[str] | None = None) -> None:
        message = f'There are no commands in the "{name}" namespace.'
        if namespaces:
            suggestions = _suggest_similar_names(name, namespaces)
            if suggestions:
                message += "\n\n" + suggestions
        super().__init__(message, code="namespace-not-found")
        self.add_note("Raised when called namespace has no commands.")

class InvalidArgument(_Trimmable, TypeError):
    """Used to indicate that the arguments to a Hypothesis function were in
    some manner incorrect.""

"""

class InvalidDefinition(_Trimmable, TypeError):
    """Used to indicate that a class definition was not well put together and
    has something wrong with it."""


class CleosWarning(CleoError, Warning):
    """A generic warning issued by Hypothesis."""


# @contextlib.contextmanager
# def add_exc_note(note: str):
#     try:
#         yield
#     except Exception as err:
#         err.add_note(note)
#         raise
#
# with add_exc_note(f"While attempting to frobnicate {item=}"):
#     frobnicate_or_raise(item)





def _suggest_similar_names(name: str, names: list[str]) -> str | None:
    if not names:
        return None

    suggested_names = find_similar_names(name, names)

    if not suggested_names:
        return None

    newline_separator = "\n    "
    return "Did you mean " + newline_separator.join(
        (
            ("this?" if len(suggested_names) == 1 else "one of these?"),
            newline_separator.join(suggested_names),
        )
    )
