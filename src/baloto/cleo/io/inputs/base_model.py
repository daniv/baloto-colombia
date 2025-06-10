# - Project   : baloto-colombia
# - User Naem : solma
# - File Name : base_model.py
# - Dir Path  : src/baloto/cleo/io/inputs
# - Created on: 2025-05-30 at 01:34:21

from __future__ import annotations

import re
from abc import ABC
from collections.abc import Sequence
from typing import Annotated
from typing import Any
from typing import Callable
from typing import LiteralString
from typing import TYPE_CHECKING
from typing import cast

from annotated_types import doc
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import StringConstraints
from pydantic import ValidationError
from pydantic import WrapValidator
from pydantic_core import PydanticCustomError

from baloto.utils.types import OptionalStr

if TYPE_CHECKING:
    from pydantic_core.core_schema import ValidationInfo


__all__ = ("BaseInputModel", "CALL_CONFIG", "AnnotatedNameString")


CALL_CONFIG = ConfigDict(arbitrary_types_allowed=True, strict=True)
_re_special_symbols = re.compile(r"^[^0-9~`!@#$%° ^&*()_+={[}\]|:;\"<>/?]*$")


def special_chars_error_validator(
    exc_factory: Callable[[str | None, ValidationError], ValueError],
) -> Any:

    def _validator(v: Any, next_: Any, ctx: ValidationInfo) -> Any:
        try:
            r = next_(v, ctx)
            return r
        except* ValidationError as e:
            for exc in e.exceptions:
                for error in exc.errors():
                    if error.get("type") == "string_pattern_mismatch":
                        raise exc_factory(ctx.field_name, exc) from None
                    else:
                        raise exc

    return WrapValidator(_validator)


class SpecialCharsValidationError(PydanticCustomError):
    template: str = "The field '{value}' cannot contain special symbols and/or white-space."

    @classmethod
    def from_validator_exc(cls, field_name: str | None, exc: ValidationError) -> ValueError:
        error = exc.errors()[0]
        error_type = cast(LiteralString, error.get("type"))
        error["ctx"]["value"] = field_name
        return cls(error_type, cast(LiteralString, cls.template), error["ctx"])


AnnotatedNameString = Annotated[
    str,
    StringConstraints(
        min_length=2,
        max_length=12,
        to_lower=True,
        strict=True,
        strip_whitespace=True,
        pattern=_re_special_symbols,
    ),
    special_chars_error_validator(SpecialCharsValidationError.from_validator_exc),
    doc("The name of the argument or option"),
]


class BaseInputModel(BaseModel, ABC):
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True,
        hide_input_in_errors=False,
    )

    name: AnnotatedNameString = Field(..., frozen=True)
    is_list: bool = Field(False, frozen=True)
    description: OptionalStr = Field("", frozen=True)
    default: str | list[str] | bool | None = Field(None)
    choices: Sequence[str] | None = Field(None, frozen=True)

    @property
    def has_choices(self) -> bool:
        return bool(self.choices)
