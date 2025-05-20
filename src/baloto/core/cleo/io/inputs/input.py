from __future__ import annotations

import re
from abc import ABC, abstractmethod

from typing import Any, TYPE_CHECKING
from typing import TextIO

from baloto.core.cleo._compat import shell_quote
from baloto.core.cleo.exceptions import CleoMissingArgumentsError
from baloto.core.cleo.exceptions import CleoValueError
from baloto.core.cleo.io.inputs.definition import Definition


if TYPE_CHECKING:
    from baloto.core.cleo.io.inputs.option import Option
    from baloto.core.cleo.io.inputs.argument import Argument


class Input(ABC):
    """
    This class is the base class for concrete Input implementations.
    """

    def __init__(self, definition: Definition | None = None) -> None:
        self._definition: Definition
        self._stream: TextIO = None  # type: ignore[assignment]
        self._options: dict[str, Any] = {}
        self._arguments: dict[str, Any] = {}
        self._interactive: bool | None = None

        if definition is None:
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
    def first_argument(self) -> str | None: ...

    @property
    @abstractmethod
    def script_name(self) -> str | None: ...

    @property
    def interactive(self) -> bool:
        return True if self._interactive is None else self._interactive

    @interactive.setter
    def interactive(self, interactive: bool = True) -> None:
        self._interactive = interactive

    def read(self, length: int, default: str = "") -> str:
        """
        Reads the given amount of characters from the input stream.
        """
        ...

    def read_line(self, length: int = -1, default: str = "") -> str:
        """
        Reads a line from the input stream.
        """

    def close(self) -> None:
        """
        Closes the input.
        """

    def is_closed(self) -> bool:
        """
        Returns whether the input is closed.
        """

    def bind(self, definition: Definition) -> None:
        """
        Binds the current Input instance with
        the given definition's arguments and options.
        """

    def validate(self) -> None:
        ...

    def argument(self, name: str) -> Argument:
        ...

    def set_argument(self, name: str, value: Any) -> None:
        ...

    def has_argument(self, name: str) -> bool:
        ...

    def option(self, name: str) -> Option:
        ...

    def set_option(self, name: str, value: Any) -> None:
        ...

    def has_option(self, name: str) -> bool:
        ...

    def escape_token(self, token: str) -> str:
        ...

    @abstractmethod
    def has_parameter_option(self, values: str | list[str], only_params: bool = False) -> bool:
        """
        Returns true if the raw parameters (not parsed) contain a value.
        """

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

    @abstractmethod
    def _parse(self) -> None: ...




