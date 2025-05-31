from __future__ import annotations

from typing import Any, TYPE_CHECKING

from pydantic import Field

from baloto.cleo.exceptions.errors import CleoLogicError
from baloto.cleo.io.inputs.base_model import BaseInputModel

if TYPE_CHECKING:
    from collections.abc import Sequence


class Argument(BaseInputModel):
    required: bool = Field(True, frozen=True)

    def model_post_init(self, __context: Any) -> None:
        default = self.default
        if self.required and self.default is not None:
            msg = "Cannot set a default value for required arguments."
            raise CleoLogicError(msg, code="arg-default-on-required")

        if self.is_list:
            if self.default is None:
                default = []
            elif not isinstance(self.default, list):
                msg = "A default value for a list argument must be a list."
                raise CleoLogicError(msg, code="arg-default-not-list-type")

        self.default = default

    def __rich__(self) -> str:
        return f"{type(self).__name__}([bold cyan]{self._name!r}[/])"

    @classmethod
    def make(
        cls,
        name: str,
        *,
        required: bool = True,
        is_list: bool = False,
        description: str | None = None,
        default: str | list[str] | None = None,
        choices: Sequence[str] | None = None,
    ):
        return cls(
            name=name, required=required, is_list=is_list, description=description, default=default, choices=choices
        )

    def __str__(self) -> str:
        return f"{self.name} required={self.required}, is_list={self.is_list}"

    def __repr__(self):
        return f"<{type(self).__name__} {self.name!r} {self.required!r} {self.is_list!r}>"
