# Project : baloto-colombia
# File Name : cli_input.py
# Dir Path : src/baloto/cleo/io/inputs
# Created on: 2025–06–08 at 04:48:12.

from __future__ import annotations

import re
from abc import abstractmethod
from typing import Any
from typing import TYPE_CHECKING
from typing import TextIO

from baloto.cleo.exceptions.errors import CleoMissingArgumentsError
from baloto.cleo.exceptions.errors import CleoValueError
from baloto.cleo.io.inputs.input import Input
from baloto.cleo.utils import shell_quote

if TYPE_CHECKING:
    from baloto.cleo.io.inputs.definition import Definition


__all__ = ("DefinitionInput", )


class DefinitionInput(Input):
    """
    This class is the base class for concrete Input implementations.
    """

    def __init__(self, definition: Definition | None = None) -> None:
        super().__init__()
        self._stream: TextIO = None  # type: ignore[assignment]
        self._definition: Definition
        self._options: dict[str, Any] = {}
        self._arguments: dict[str, Any] = {}

        if definition is None:
            from baloto.cleo.io.inputs.definition import Definition

            self._definition = Definition()
        else:
            self.bind(definition)
            self.validate()

    @property
    def arguments(self) -> dict[str, Any]:
        return {**self._definition.argument_defaults, **self._arguments}

    @property
    def options(self) -> dict[str, Any]:
        return {**self._definition.option_defaults, **self._options}

    @property
    def stream(self) -> TextIO:
        return self._stream

    @stream.setter
    def stream(self, stream: TextIO) -> None:
        self._stream = stream

    @property
    @abstractmethod
    def first_argument(self) -> str | None:
        raise NotImplementedError("[c1]first_argument[/] is an abstract method")

    @property
    @abstractmethod
    def script_name(self) -> str | None:
        raise NotImplementedError("[c1]script_name[/] is an abstract method")

    def read(self, length: int, default: str = "") -> str:
        """
        Reads the given amount of characters from the input stream.
        """
        if not self.is_interactive():
            return default

        return self._stream.read(length)

    def read_line(self, length: int = -1, default: str = "") -> str:
        """
        Reads a line from the input stream.
        """
        if not self.is_interactive():
            return default

        return self._stream.readline(length)

    def close(self) -> None:
        """
        Closes the input.
        """
        self._stream.close()

    def is_closed(self) -> bool:
        """
        Returns whether the input is closed.
        """
        return self._stream.closed

    def bind(self, definition: Definition) -> None:
        """
        Binds the current Input instance with
        the given definition's arguments and options.
        """
        self._arguments = {}
        self._options = {}
        self._definition = definition

        self._parse()

    def validate(self) -> None:
        missing_arguments = [
            argument.name
            for argument in self._definition.arguments()
            if argument.name not in self._arguments and argument.required
        ]

        if missing_arguments:
            raise CleoMissingArgumentsError(
                f'Not enough arguments (missing: "{", ".join(missing_arguments)}")'
            )

    def argument(self, name: str) -> Any:
        if not self._definition.has_argument(name):
            raise CleoValueError(f'The argument "{name}" does not exist')

        if name in self._arguments:
            return self._arguments[name]

        return self._definition.argument(name).default

    def set_argument(self, name: str, value: Any) -> None:
        if not self._definition.has_argument(name):
            raise CleoValueError(f'The argument "{name}" does not exist')

        self._arguments[name] = value

    def has_argument(self, name: str) -> bool:
        return self._definition.has_argument(name)

    def option(self, name: str) -> Any:
        if not self._definition.has_option(name):
            raise CleoValueError(f'The option "--{name}" does not exist')

        if name in self._options:
            return self._options[name]

        return self._definition.option(name).default

    def set_option(self, name: str, value: Any) -> None:
        if not self._definition.has_option(name):
            raise CleoValueError(f'The option "--{name}" does not exist')

        self._options[name] = value

    def has_option(self, name: str) -> bool:
        return self._definition.has_option(name)

    @staticmethod
    def escape_token(token: str) -> str:
        if re.match(r"^[\w-]+$", token):
            return token

        return shell_quote(token)

    @abstractmethod
    def has_parameter_option(self, values: str | list[str], only_params: bool = False) -> bool:
        """
        Returns true if the raw parameters (not parsed) contain a value.
        """
        raise NotImplementedError("[c1]has_parameter_option[/] is an abstract method")

    @abstractmethod
    def parameter_option(
        self,
        values: str | list[str],
        default: Any = False,
        only_params: bool = False,
    ) -> Any:
        """
        Returns the value of a raw option (not parsed).
        """
        raise NotImplementedError("[c1]parameter_option[/] is an abstract method")

    @abstractmethod
    def _parse(self) -> None:
        raise NotImplementedError("[c1]_parse[/] is an abstract method")
