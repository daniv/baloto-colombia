from __future__ import annotations

from typing import Any, Annotated, TYPE_CHECKING, Callable, TypeAliasType

from annotated_types import Gt
from mypy.typeops import custom_special_method
from pydantic import BaseModel, ConfigDict, StringConstraints, WrapValidator, ValidationInfo, ValidationError, Field
from rich.table import Table
from baloto.cleo.exceptions import CleoLogicError

if TYPE_CHECKING:
    from rich.console import Console, ConsoleOptions, RenderResult, ConsoleRenderable


PositiveIntList = TypeAliasType('PositiveIntList', list[Annotated[int, Gt(0)]])
"""
1 validation error for class 'Argument'

ERROR-1
msg : String should have at least 2 characters
type: string_too_short
input: f
field name: loc["field_name"]
url = 

******
1 validation error for ValidatorCallable
ValidationInfo(config={'title': 'Argument', 'extra_fields_behavior': 'forbid', 'str_strip_whitespace': True, 'strict': True}, context=None, data={}, field_name='name')
  String should have at least 2 characters [type=string_too_short, input_value='f', input_type=str]
    For further information visit https://errors.pydantic.dev/2.11/v/string_too_short
"""

def custom_error_msg(exc_factory: Callable[[str | None, Exception], Exception]) -> Any:
    def _validator(v: Any, next_: Any, ctx: ValidationInfo) -> Any:
        try:
            r = next_(v, ctx)
            return r
        except ValidationError as e:
            raise exc_factory(ctx.field_name, e) from None

    return WrapValidator(_validator)


NameString = Annotated[
    str,
    StringConstraints(
        min_length=2
    ),
    # custom_error_msg(NameValidationError.from_validator_exc)
]


"""

"1 validation error for class Argument
name
  Value error, The field name can not contain special symbols. [type=value_error, input_value='f', input_type=str]
    For further information visit https://errors.pydantic.dev/2.11/v/value_error"
    
name
  String should have at least 2 characters [type=string_too_short, input_value='f', input_type=str]
    For further information visit https://errors.pydantic.dev/2.11/v/string_too_short

"""
"""
1 validation error for Argument
name
  String should have at least 2 characters [type=string_too_short, input_value='f', input_type=str]
    For further information visit https://errors.pydantic.dev/2.11/v/string_too_short
"""
class Argument(BaseModel):
    model_config = ConfigDict(
        extra="forbid", validate_assignment=True, arbitrary_types_allowed=True,
        str_strip_whitespace=True, strict=True
    )
    # name: Annotated[str,
    #     StringConstraints(
    #         strip_whitespace=True, to_upper=True, pattern=r'^[a-z]+$',
    #         to_lower=True, strict=True, min_length=2, max_length=10
    #     ),
    # ]
    name: NameString = Field(...,frozen=True)
    required: bool = Field(True, frozen=True)
    is_list: bool = Field(False, frozen=True)
    description: str | None = Field("", frozen=True)
    default: Any | None = Field(None)
    choices: list[str] | None = Field(None)

    @classmethod
    def new(
        cls,
        name: str,
        *,
        required: bool = True,
        is_list: bool = False,
        description: str | None = None,
        default: Any | None = None,
        choices: list[str] | None = None,
    ) -> Argument:
        try:
            return Argument(
                name=name, required=required, is_list=is_list,
                description=description, default=default, choices=choices
            )
        except ValidationError as exc_info:
            t = exc_info.title
            args = exc_info.args
            ec = exc_info.error_count()
            as_json = exc_info.json()
            exc_info.add_note("fff")
            for error in exc_info.errors(include_input=True, include_context=True, include_url=True):
                er = error


        # except ValidationError as e:
        #     from baloto.cleo.exceptions import CleoValidationError, CleoValidationError2
        #     cve = CleoValidationError(e)
        #     cve = CleoValidationError2(e)
        #     raise e from e

    @property
    def has_choices(self) -> bool:
        return bool(self.choices)

    def model_post_init(self, __context: Any) -> None:
        default = self.default
        if self.required and self.default is not None:
            raise CleoLogicError("Cannot set a default value for required arguments")

        if self.is_list:
            if self.default is None:
                default = []
            elif not isinstance(self.default, list):
                raise CleoLogicError("A default value for a list argument must be a list")

        self.default = default

    def _render_validation_error(self) -> ConsoleRenderable:

    def __rich__(self) -> str:
        return f"Argument([bold cyan]{self._name!r}[/])"

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> RenderResult:
        yield f"[b]Student:[/b] #{self.id}"
        my_table = Table("Attribute", "Value")
        my_table.add_row("name", self.name)
        my_table.add_row("age", str(self.age))
        yield my_table




class Argumento:
    """
    A command line argument.
    """

    def __init__(
        self,
        name: str,
        required: bool = True,
        is_list: bool = False,
        description: str | None = None,
        default: Any | None = None,
        choices: list[str] | None = None,
    ) -> None:
        name = name.strip()
        if not name:
            raise CleoValueError("An argument name cannot be empty")
        if " " in name:
            raise CleoValueError("An argument name cannot have withspace")
        self._name = name
        self._required = required
        self._is_list = is_list
        self._description = description or ""
        self._default: str | list[str] | None = None
        self._choices = choices

        self.set_default(default)

    @property
    def name(self) -> str:
        return self._name

    @property
    def default(self) -> str | list[str] | None:
        return self._default

    @property
    def description(self) -> str:
        return self._description

    @property
    def choices(self) -> list[str] | None:
        return self._choices

    @property
    def has_choices(self) -> bool:
        return bool(self._choices)

    def is_required(self) -> bool:
        return self._required

    def is_list(self) -> bool:
        return self._is_list

    def set_default(self, default: Any | None = None) -> None:
        if self._required and default is not None:
            raise CleoLogicError("Cannot set a default value for required arguments")

        if self._is_list:
            if default is None:
                default = []
            elif not isinstance(default, list):
                raise CleoLogicError("A default value for a list argument must be a list")

        self._default = default

    def __repr__(self) -> str:
        return (
            f"Argument({self._name!r}, "
            f"required={self._required}, "
            f"is_list={self._is_list}, "
            f"description={self._description!r}, "
            f"default={self._default!r}), "
            f"choices={self._choices!r})"
        )


