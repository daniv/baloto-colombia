from __future__ import annotations

from baloto.core.cleo import helpers
from baloto.core.cleo.io.inputs.argv_input import ArgvInput


class StringInput(ArgvInput):
    """
    Represents an input provided as a string
    """

    def __init__(self, input: str) -> None:
        super().__init__([])
        self._set_tokens(self.tokenize(input))

    @staticmethod
    def tokenize(input: str) -> list[str]:
        return helpers.tokenize(input)
