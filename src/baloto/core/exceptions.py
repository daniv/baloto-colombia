from __future__ import annotations

import dataclasses
import shlex

from dataclasses import InitVar
from subprocess import CalledProcessError
from typing import TYPE_CHECKING

from baloto.core.cleo.exceptions import CleoError

from baloto.core.utils.compat import decode
from baloto.core.utils.console_message import ConsoleMessage


if TYPE_CHECKING:
    from cleo.io.io import IO


class BalotoConsoleError(CleoError):
    pass


class GroupNotFoundError(BalotoConsoleError):
    pass


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
        Write the error text to the provided IO iff there is any text to write.
        """
        if text := self.get_text(debug=io.is_verbose(), strip=False):
            io.error_output.write(text)

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
                f"{indent}You can also run your [c1]baloto[/] command with {verbosity} "
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
            ).wrap("info"),
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
