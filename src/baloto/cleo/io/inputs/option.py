# - Project   : baloto-colombia
# - User Naem : solma
# - File Name : option.py
# - Dir Path  : src/baloto/cleo/io/inputs
# - Created on: 2025-05-30 at 01:08:44

from __future__ import annotations

import re
from typing import Any, cast, LiteralString, Sequence
from typing import TYPE_CHECKING

from pydantic import Field, field_validator, TypeAdapter

from baloto.cleo.exceptions.errors import CleoLogicError, CleoValueError
from baloto.cleo.io.inputs.base_model import AnnotatedNameString, BaseInputModel
from baloto.utils.types import OptionalStr

if TYPE_CHECKING:
    pass


class Option(BaseInputModel):
    """
    A command line option.
    """

    name: AnnotatedNameString = Field(..., frozen=False)
    shortcut: OptionalStr = Field(None, frozen=True)
    flag: bool = Field(True, frozen=True)
    requires_value: bool = Field(True)

    @field_validator("name", mode="before")
    @classmethod
    def remove_hyphens(cls, value: str) -> Any:
        if value.startswith("--"):
            return value[2:]
        return value

    @field_validator("shortcut", mode="before")
    @classmethod
    def remove_hyphen(cls, value: str) -> Any:
        if value is not None:
            shortcuts = re.split(r"\|-?", value.lstrip("-"))
            value = "|".join(filter(None, shortcuts))

            if not value:
                msg = "An option shortcut cannot be empty"
                err = CleoValueError(msg)
                from pydantic_core import PydanticCustomError

                raise PydanticCustomError("shortcut-not-set", cast(LiteralString, msg), {"error": err})
        return value

    def model_post_init(self, __context: Any) -> None:

        # if self.shortcut is not None:
        #     shortcuts = re.split(r"\|-?", self.shortcut.lstrip("-"))
        #     shortcut = "|".join(filter(None, shortcuts))
        #
        #     if not shortcut:
        #         msg = "An option shortcut cannot be empty"
        #         err = CleoValueError(msg)
        #         from pydantic_core import PydanticCustomError
        #
        #         raise PydanticCustomError("shortcut-not-set", cast(LiteralString, msg), {"error": err})

        if self.is_list and self.flag:
            raise CleoLogicError("A flag option cannot be a list as well.", code="opt-flag-list-type")

        default = self.default
        if self.flag and default is not None:
            raise CleoLogicError("A flag option cannot have a default value.", code="opt-flag-with-default")

        if self.is_list:
            if default is None:
                default = []
            elif not isinstance(default, list):
                raise CleoLogicError(
                    "A default value for a list option must be a list.", code="opt-default-not-list-type"
                )
        # elif self.is_list is False and default is not None:
        #     if isinstance(default, list):
        #         raise CleoLogicError(
        #             "A default value for a non-list option should not be a list.",
        #             code="opt-default-list-type"
        #         )

        if self.choices and self.default is not None:
            # TODO: check for list with choices
            # if self.is_list and
            # adapter = self._get_adapter()
            # adapter.validate_python(self.choices, strict=True)
            if default not in self.choices:
                raise CleoLogicError("A default value must be in choices.", code="default-not-in-choices")

        if self.choices and self.flag:
            raise CleoLogicError("A flag option cannot have choices.", code="opt-choices-on-flag")

        if self.choices and not self.is_value_required():
            raise CleoLogicError("An option with choices requires a value.", code="opt-choices-required-value")

        if self.flag:
            default = False

        self.default = default

    @property
    def is_flag(self) -> bool:
        return self.flag

    @property
    def accepts_value(self) -> bool:
        return not self.flag

    def is_value_required(self) -> bool:
        return not self.flag and self.requires_value

    def _get_adapter(self) -> TypeAdapter[Any]:
        if isinstance(self.default, list):
            if all(isinstance(val, str) for val in self.default):
                adapter = TypeAdapter(Sequence[str])
            elif all(isinstance(val, int) for val in self.default):
                adapter = TypeAdapter(Sequence[int])
            else:
                adapter = TypeAdapter(Sequence[float])
        else:
            default_type = type(self.default)
            adapter = TypeAdapter(Sequence[default_type])
        return adapter

    @classmethod
    def make(
        cls,
        name: str,
        shortcut: str | None = None,
        *,
        is_list: bool = False,
        description: str = "",
        default: Any | None = None,
        choices: list[str] | None = None,
        flag: bool = True,
        requires_value: bool = True,
    ) -> Option:
        return cls(
            name=name,
            shortcut=shortcut,
            is_list=is_list,
            description=description,
            default=default,
            choices=choices,
            flag=flag,
            requires_value=requires_value,
        )

    def __str__(self) -> str:
        sh = self.shortcut or ""
        return f"--{self.name} -{sh} requires_value={self.requires_value}, is_list={self.is_list}, flag={self.flag}"

    def __repr__(self):
        return f"<{type(self).__name__} {self.name!r} {self.shortcut!r}>"
