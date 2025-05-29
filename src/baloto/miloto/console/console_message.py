from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Any, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    StringConstraints,
    BeforeValidator,
    Field,
    computed_field,
    validate_call,
    PrivateAttr,
)
from rich._loop import loop_last
from rich.style import StyleType
from rich.text import Text
from rich.style import Style

if TYPE_CHECKING:
    pass


def validate_text_not_empty(value: str) -> str:
    text = Text.from_markup(value)
    if len(text.plain) <= 1:
        return text.plain
    return text.markup


class ConsoleMessage(BaseModel):

    model_config = ConfigDict(
        extra="forbid", validate_assignment=True, arbitrary_types_allowed=True, strict=True
    )

    message: Annotated[
        str, StringConstraints(min_length=1, strict=True), BeforeValidator(validate_text_not_empty)
    ]
    style: StyleType | None = Field("")
    debug: bool = False

    _text: str = PrivateAttr(default="")
    _rich_text: Text | None = PrivateAttr(None)
    _section_flag: bool = PrivateAttr(False)

    def model_post_init(self, __context: Any) -> None:
        self._rich_text = Text.from_markup(self.message, style=self.style)
        self._text = self._rich_text.markup

    @computed_field(description="the rmessage without any styles")  # type: ignore[prop-decorator]
    @property
    def plain(self) -> str:
        return self._rich_text.plain

    @property
    def text(self) -> str:
        return self._text

    @property
    def has_section(self) -> bool:
        return self._section_flag

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def indent(self, indent: str, *, style: StyleType = "") -> Self:
        lines = []

        indent_text = Text.from_markup(indent, style=style)
        split_list = self._rich_text.split("\n")

        for last, item in loop_last(split_list):
            current = Text().append(indent_text).append(item)
            if not last:
                current.append("\n")
            lines.append(current)
        self._text = Text().join(lines).markup
        self._rich_text = Text.from_markup(self._text)
        return self

    def make_section(
        self,
        title: str,
        *,
        title_style: StyleType = "",
        indent: str = "",
        indent_style: StyleType = "",
    ) -> Self:
        if not self.text:
            return self

        if not self._section_flag:
            self._section_flag = True
            indent_text = Text.from_markup(indent, style=indent_style).markup
            section = (
                [Text.from_markup(f"[b]{title}:[/]", style=title_style).markup] if title else []
            )
            section.extend(self.text.splitlines())
            self._text = f"\n{indent_text}".join(section).strip()
            self._rich_text = Text.from_markup(self._text)

        return self

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return f"<ConsoleMessage {self.message!r} {self.style!r}>"
