from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


import datetime as dt
from dataclasses import dataclass
from typing import Any, Callable, Optional


from pydantic_core import CoreSchema, core_schema

from pydantic import (
    GetCoreSchemaHandler,
    PydanticUserError,
)


@dataclass(frozen=True)
class MyDatetimeValidator:
    tz_constraint: Optional[str] = None

    def tz_constraint_validator(
        self,
        value: dt.datetime,
        handler: Callable,
    ):
        """Validate tz_constraint and tz_info."""
        # handle naive datetimes
        if self.tz_constraint is None:
            assert value.tzinfo is None, "tz_constraint is None, but provided value is tz-aware."
            return handler(value)

        # validate tz_constraint and tz-aware tzinfo
        if self.tz_constraint not in pytz.all_timezones:
            raise PydanticUserError(
                f"Invalid tz_constraint: {self.tz_constraint}",
                code="unevaluable-type-annotation",
            )
        result = handler(value)
        assert self.tz_constraint == str(
            result.tzinfo
        ), f"Invalid tzinfo: {str(result.tzinfo)}, expected: {self.tz_constraint}"

        return result

    def __get_pydantic_core_schema__(
        self,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        return core_schema.no_info_wrap_validator_function(
            self.tz_constraint_validator,
            handler(source_type),
        )


# LA = "America/Los_Angeles"
# ta = TypeAdapter(Annotated[dt.datetime, MyDatetimeValidator(LA)])
# print(ta.validate_python(dt.datetime(2023, 1, 1, 0, 0, tzinfo=pytz.timezone(LA))))
