from __future__ import annotations

import dataclasses
import re
import shlex

from dataclasses import InitVar
from subprocess import CalledProcessError
from typing import TYPE_CHECKING, Annotated, Self, Any

from rich.padding import PaddingDimensions

from baloto.core.cleo.exceptions import CleoError

from baloto.core.utils.compat import decode


if TYPE_CHECKING:
    from cleo.io.io import IO
    from rich.table import Table
    from rich.padding import Padding
    from rich.console import RenderableType


class BalotoConsoleError(CleoError):
    pass


class GroupNotFoundError(BalotoConsoleError):
    pass

def text_after_validator(text: str) -> Text:
    if isinstance(text, str):
        return Text.from_markup(text)
    return text

import dataclasses as _dataclasses


from pydantic import BaseModel, computed_field, ConfigDict, Field, StringConstraints, ValidationError, WrapValidator, \
    PlainValidator, ValidatorFunctionWrapHandler, BeforeValidator
from rich.style import Style, StyleType
from rich.text import Text, TextType


def truncate(value: Any, handler: ValidatorFunctionWrapHandler) -> str:
    try:
        return handler(value)
    except ValidationError as err:
        if err.errors()[0]['type'] == 'string_too_long':
            return handler(value[:5])
        else:
            raise

def validate_not_empty(value: str) -> str:
    text = Text.from_markup(value)
    if len(text.plain) <= 1:
        return text.plain
    return text.markup

# BeforeValidator(lambda v: Text.from_markup(v).plain)
class ConsoleMessage(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True, arbitrary_types_allowed=True, strict=True)

    message: Annotated[
        str,
        StringConstraints(min_length=1, strict=True),
        BeforeValidator(validate_not_empty)
    ]
    debug: bool = False
    style: StyleType | None = Field("")

    _text: TextType | list[TextType] | None = None
    _section: Padding | None = None

    def model_post_init(self, __context: Any) -> None:
        # self._text = Text.from_markup(self.message)
        # if self.style:
        self._text = Text.from_markup(self.message, style=self.style)

    @computed_field(description="the rmessage without any styles")  # type: ignore[prop-decorator]
    @property
    def plain(self) -> str:
        return self.text.plain

    @computed_field
    @property
    def markup(self) -> str:
        return self.text.markup

    @property
    def text(self) -> Text:
        return self._text

    @property
    def section(self) -> Padding:
        return self._section

    # type: ignore[prop-decorator]

    def indent(self, indent: str, style: StyleType = "") -> Self:

        lines = []
        indent_text = Text.from_markup(indent, style=style)
        split_list = self.text.split("\n")
        for split in split_list:
            current = Text("")
            lines.append(current.append(indent_text).append(split).append("\n"))
        self._text = Text().join(lines)
        return self

    def make_section(
            self,
            title: str,
            style: StyleType = "",
            padding: PaddingDimensions = 0,
    ) -> Self:
        from rich.table import Table
        from rich.containers import Renderables
        from rich.padding import Padding

        if self._section is not None:
            return self

        renderables = [self.text]
        output = Table.grid(padding=(0, 1), expand=True)
        output.add_column(style=style, width=len(title) + 1)
        output.add_column(ratio=1, overflow="fold", highlight=True)
        row: list[RenderableType] = []
        if title:
            row.append(Text(title, style=style))
        row.append(Renderables(renderables))

        output.add_row(*row)
        padding = Padding(output, padding)
        return padding

    def _render_as_padding(self, title: str, title_style: StyleType = "", indent: str = "") -> ConsoleRenderable:
        renderables = [self.text]
        from rich.table import Table
        output = Table.grid(padding=(0, 1), expand=True)
        output.add_column(style=title_style, width=len(title) + 1)
        output.add_column(ratio=1, overflow="fold", highlight=True)
        row: list[RenderableType] = []
        if title:
            row.append(f"[b]{title}:[/]")
        from rich.containers import Renderables
        row.append(Renderables(renderables))

        output.add_row(*row)
        from rich.padding import Padding

        return Padding(output, (0, 0, 0, len(indent)))


        # if not self.text:
        #     return self
        #
        # if self.text:
        #     section = [f"[b]{title}:[/]"] if title else []
        #     section.extend(self.text.splitlines())
        #     self.text = f"\n{indent}".join(section).strip()
        #
        # return self

    def __str__(self) -> str:
        return self.message
    #
    def __repr__(self) -> str:
        return f"<ConsoleMessage {self.message!r} {self.style!r}>"



@dataclasses.dataclass
class ConsoleMessage2:
    """
    Representation of a console message, providing utilities for formatting text
    with tags, indentation, and sections.

    The ConsoleMessage class is designed to represent text messages that might be
    displayed in a console or terminal output. It provides features for managing
    formatted text, such as stripping tags, wrapping text with specific tags,
    indenting, and creating structured message sections.
    """

    text: str
    debug: bool = False

    @property
    def stripped(self) -> str:
        from baloto.core.cleo.formatters.formatter import Formatter

        return Formatter.strip_styles(self.text)

    def wrap(self, tag: str) -> ConsoleMessage:
        if self.text:
            self.text = f"[{tag}]{self.text}[/]"
        return self

    def indent(self, indent: str) -> ConsoleMessage:
        if self.text:
            self.text = f"\n{indent}".join(self.text.splitlines()).strip()
            self.text = f"{indent}{self.text}"
        return self

    def make_section(
        self,
        title: str,
        indent: str = "",
    ) -> ConsoleMessage:
        if not self.text:
            return self

        if self.text:
            section = [f"[b]{title}:[/]"] if title else []
            section.extend(self.text.splitlines())
            self.text = f"\n{indent}".join(section).strip()

        return self


@dataclasses.dataclass
class PrettyCalledProcessError:
    """
    Represents a formatted and decorated error object for a subprocess call.

    This class is used to encapsulate information about a `CalledProcessError`,
    providing additional context such as command output, errors, and helpful
    debugging messages. It is particularly useful for wrapping and decorating
    subprocess-related exceptions in a more user-friendly format.

    Attributes:
        message: A string representation of the exception.
        output: A section formatted representation of the exception stdout.
        errors: A section formatted representation of the exception stderr.
        command_message: Formatted message including a hint on retrying the original command.
        command: A `shelex` quoted string representation of the original command.
        exception: The original `CalledProcessError` instance.
        indent: Indent prefix to use for inner content per section.
    """

    message: ConsoleMessage = dataclasses.field(init=False)
    output: ConsoleMessage = dataclasses.field(init=False)
    errors: ConsoleMessage = dataclasses.field(init=False)
    command_message: ConsoleMessage = dataclasses.field(init=False)
    command: str = dataclasses.field(init=False)
    exception: InitVar[CalledProcessError] = dataclasses.field(init=True)
    indent: InitVar[str] = dataclasses.field(default="")

    def __post_init__(self, exception: CalledProcessError, indent: str) -> None:
        self.message = ConsoleMessage(str(exception).strip(), debug=True).make_section(
            "Exception", indent
        )
        self.output = ConsoleMessage(decode(exception.stdout), debug=True).make_section(
            "Output", indent
        )
        self.errors = ConsoleMessage(decode(exception.stderr), debug=True).make_section(
            "Errors", indent
        )
        self.command = (
            shlex.join(exception.cmd) if isinstance(exception.cmd, list) else exception.cmd
        )
        self.command_message = ConsoleMessage(
            f"You can test the failed command by executing:\n\n    [command]{self.command}[/]",
            debug=False,
        )


class BalotoRuntimeError(BalotoConsoleError):
    """
    Represents a runtime error in the Poetry console application.
    """

    def __init__(
        self,
        reason: str,
        messages: list[ConsoleMessage] | None = None,
        exit_code: int = 1,
    ) -> None:
        super().__init__(reason)
        self.exit_code = exit_code
        self._messages = messages or []
        self._messages.insert(0, ConsoleMessage(reason))

    def write(self, io: IO) -> None:
        """
        Write the error text to the provided IO iff there is any text
        to write.
        """
        if text := self.get_text(debug=io.is_verbose(), strip=False):
            text = f"[error]{text}[/error]"
            io.write_error(text)

    def get_text(self, debug: bool = False, indent: str = "", strip: bool = False) -> str:
        """
        Convert the error messages to a formatted string. All empty messages
        are ignored along with debug level messages if `debug` is `False`.
        """
        text = ""
        has_skipped_debug = False

        for message in self._messages:
            if message.debug and not debug:
                has_skipped_debug = True
                continue

            message_text = message.stripped if strip else message.text
            if not message_text:
                continue

            if indent:
                message_text = f"\n{indent}".join(message_text.splitlines())

            text += f"{indent}{message_text}\n{indent}\n"

        if has_skipped_debug:
            verbosity = "[switch]-v|-vv|-vvv[/]"
            message = ConsoleMessage(
                f"{indent}You can also run your [c1]poetry[/] command with {verbosity}, "
                f"to see more information.\n{indent}\n"
            )
            text += message.stripped if strip else message.text

        return text.rstrip(f"{indent}\n")

    def __str__(self) -> str:
        return self._messages[0].stripped.strip()

    @classmethod
    def create(
        cls,
        reason: str,
        exception: CalledProcessError | Exception | None = None,
        info: list[str] | str | None = None,
    ) -> BalotoRuntimeError:
        """
        Create an instance of this class using the provided reason. If
        an exception is provided, this is also injected as a debug
        `ConsoleMessage`.

        There is specific handling for known exception types. For example,
        if exception is of type `subprocess.CalledProcessError`, the following
        sections are additionally added when available - stdout, stderr and
        command for testing.
        """
        if isinstance(info, str):
            info = [info]

        messages: list[ConsoleMessage] = [
            ConsoleMessage(
                "\n".join(info or []),
                debug=False,
            )
            .make_section(f"Exception message")
            .indent("    - ")
            .wrap("error"),
        ]

        if isinstance(exception, CalledProcessError):
            error = PrettyCalledProcessError(exception, indent="    | ")
            messages = [
                error.message.wrap("warning"),
                error.output.wrap("warning"),
                error.errors.wrap("warning"),
                *messages,
                error.command_message,
            ]
        elif exception is not None and isinstance(exception, Exception):
            messages.insert(
                0,
                ConsoleMessage(str(exception), debug=True).make_section(
                    "Exception", indent="    | "
                ),
            )

        return cls(reason, messages)

    def append(self, message: str | ConsoleMessage) -> BalotoRuntimeError:
        if isinstance(message, str):
            message = ConsoleMessage(message)
        self._messages.append(message)
        return self
