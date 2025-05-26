from __future__ import annotations

from baloto.core.cleo.utils import find_similar_names

from rich.panel import Panel


class CleoError(Exception):
    """
    Base Cleo exception.
    """

    exit_code: int | None = None


class CleoLogicError(CleoError):
    """
    Raised when there is error in command arguments
    and/or options configuration logic.
    """


class CleoRuntimeError(CleoError):
    """
    Raised when command is called with invalid options or arguments.
    """


class CleoValueError(CleoError):
    """
    Raised when wrong value was given to Cleo components.
    """


class CleoNoSuchOptionError(CleoError):
    """
    Raised when command does not have given option.
    """


class CleoUserError(CleoError):
    """
    Base exception for user errors.
    """


class CleoMissingArgumentsError(CleoUserError):
    """
    Raised when called command was not given required arguments.
    """


def _suggest_similar_names(name: str, names: list[str]) -> str | None:
    if not names:
        return None

    suggested_names = find_similar_names(name, names)

    if not suggested_names:
        return None

    newline_separator = "\n    "
    return "Did you mean " + newline_separator.join(
        (
            ("this?" if len(suggested_names) == 1 else "one of these?"),
            newline_separator.join(suggested_names),
        )
    )


class CleoCommandNotFoundError(CleoUserError):
    """
    Raised when called command does not exist.
    """

    def __init__(self, name: str, commands: list[str] | None = None) -> None:
        message = f'The command "{name}" does not exist.'
        if commands:
            suggestions = _suggest_similar_names(name, commands)
            if suggestions:
                message += "\n\n" + suggestions
        super().__init__(message)


class CleoNamespaceNotFoundError(CleoUserError):
    """
    Raised when called namespace has no commands.
    """

    def __init__(self, name: str, namespaces: list[str] | None = None) -> None:
        message = f'There are no commands in the "{name}" namespace.'
        if namespaces:
            suggestions = _suggest_similar_names(name, namespaces)
            if suggestions:
                message += "\n\n" + suggestions
        super().__init__(message)


class CleoCommandError(Exception):
    def __init__(self, msg: str, title: str = "", command_name: str = "") -> None:
        super().__init__(msg)
        self.msg = msg
        self.title = title
        self.command_name = command_name


def pretty_print_error(error: CleoCommandError) -> None:
    from rich import print as rich_print

    rich_print(pretty_error_message(error))


def pretty_error_message(error: CleoCommandError) -> Panel:
    from rich.columns import Columns

    error_col = Columns(
        [str(error), error.command_name],
        column_first=True
    )

    return Panel.fit(
        error_col,
        title=error.title if error.title else "Baloto encountered an error.",
        title_align="left",
        border_style="red",
    )


def pretty_print_warning(title: str, message: str) -> None:
    from rich import print as rich_print


    # Columns(
    #     [message, ],
    #     column_first=
    # )

    rich_print(
        Panel.fit(
            message,
            title=title,
            title_align="left",
            border_style="green",
        )
    )
