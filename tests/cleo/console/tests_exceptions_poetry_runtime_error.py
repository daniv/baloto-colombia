from __future__ import annotations

import itertools
import re
from subprocess import CalledProcessError
from turtledemo.penrose import start
from typing import TYPE_CHECKING
from typing import cast

import pytest
from _pytest.fixtures import FixtureRequest

from baloto.core.cleo.io.outputs.output import Verbosity
from baloto.core.exceptions import BalotoRuntimeError
from baloto.core.utils.console_message import ConsoleMessage

from tests.utils import print_section_rule

if TYPE_CHECKING:
    from baloto.core.cleo.io.outputs.console_output import ConsoleOutput
    from rich.console import Console
    from baloto.core.cleo.io.io import IO


# Common error messages
ERROR_MESSAGE_NOTE = (
    "[b]Note:[/] This error arises from interacting with "
    "the specified vcs source and is likely not a "
    "Poetry issue."
)
ERROR_MESSAGE_PROBLEMS_SECTION_START = (
    "This issue could be caused by any of the following;\n\n"
    "- there are network issues in this environment"
)
ERROR_MESSAGE_BAD_REVISION = (
    "- the revision ({revision}) you have specified\n"
    "    - was misspelled\n"
    "    - is invalid (must be a sha or symref)\n"
    "    - is not present on remote"
)


@pytest.mark.parametrize(
    ("reason", "messages", "exit_code", "expected_reason"),
    [
        ("Error occurred!", None, 1, "Error occurred!"),  # Default scenario
        (
            "Specific error",
            [ConsoleMessage("Additional details.")],
            2,
            "Specific error",
        ),  # Custom exit code and messages
        ("Minimal error", [], 0, "Minimal error"),  # No additional messages
    ],
    ids=["error-ocurred", "Specific error", "minimal-error"],
)
def baloto_runtime_error_init_test(
    reason: str,
    messages: list[ConsoleMessage] | None,
    exit_code: int,
    expected_reason: str,
) -> None:
    """Test the basic initialization of the PoetryRuntimeError class."""
    error = BalotoRuntimeError(reason, messages, exit_code)
    assert error.exit_code == exit_code
    assert str(error) == expected_reason
    assert isinstance(error._messages[0], ConsoleMessage)
    assert error._messages[0].text == reason


def baloto_runtime_error_get_text_test(error_console_output: ConsoleOutput) -> None:
    # import random
    #
    # range_list = list(range(1, 40))
    # excluded_list = list(filter(lambda x: x not in [2, 10, 12, 27], range_list))
    # random.shuffle(excluded_list)
    # batched_list = list(itertools.batched(excluded_list, 5))
    # print(" ")
    # for row in batched_list:
    #     sorted_list = sorted(list(row))
    #     print(sorted_list)

    msgs = {
        "basic": ConsoleMessage("Basic message"),
        "debug": ConsoleMessage("Debug message", debug=True),
        "info": ConsoleMessage("Info message"),
        "tagged_b": ConsoleMessage("[bold deep_sky_blue1]Tagged Bolded message[/]"),
        "debug_i": ConsoleMessage("[italic blue dim]Debug Tagged Italics Message[/]", debug=True),
        "err": ConsoleMessage("Error occurred!"),
    }

    # -- Debug message ignored
    messages = [msgs["basic"], msgs["debug"]]
    error = BalotoRuntimeError("Error", messages)
    text = error.get_text(debug=False, strip=False)
    error_console_output.console.rule("Debug message ignored")
    error_console_output.write(text, new_line_start=True)

    # -- Debug message included in verbose mode
    text = error.get_text(debug=True, strip=False)
    error_console_output.write(text, new_line_start=True)

    # -- Stripped tags and debug message
    messages = [msgs["tagged_b"], msgs["debug_i"]]
    error = BalotoRuntimeError("Error", messages)
    text = error.get_text(debug=True, strip=True)

    error_console_output.write(text, new_line_start=True)

    # -- unstripped tags and debug message
    text = error.get_text(debug=True, strip=False)
    error_console_output.write(text, new_line_start=True)

    # -- tags and no debug message
    text = error.get_text(debug=False, strip=False)
    error_console_output.write(text, new_line_start=True)

    # -- Indented message
    messages = [msgs["err"]]
    error = BalotoRuntimeError("Error", messages)
    text = error.get_text(debug=False, strip=False, indent="    ")
    error_console_output.console.rule("Indented message")
    error_console_output.write(text, new_line_start=True)


def poetry_runtime_error_create_test(error_console_output: ConsoleOutput, baloto_io: IO) -> None:

    # argv_input =
    # original_input = cast("ArgvInput", io.input)
    # # noinspection PyProtectedMember
    # tokens: list[str] = original_input._tokens
    #
    # parser = argparse.ArgumentParser(add_help=False)

    c = error_console_output.console
    c.line()

    # -- Command failed, no-exception, no-info
    error = BalotoRuntimeError.create(reason="Command failed")
    print_section_rule(c, "Command failed, no-exception, no-info")
    error.write(baloto_io)

    # -- Exception message included (raise verbosity)
    current_varbosity = error_console_output.verbosity
    error = BalotoRuntimeError.create(
        reason="Command failure",
        exception=ValueError("The value entered is grater than 100"),
    )
    print_section_rule(c, "Exception message included")
    try:
        baloto_io.set_verbosity(Verbosity.VERBOSE)
        error.write(baloto_io)
    finally:
        baloto_io.set_verbosity(current_varbosity)

    # -- Subprocess error
    error = BalotoRuntimeError.create(
        reason="Subprocess error",
        exception=CalledProcessError(1, ["cmd"], b"stdout", b"stderr"),
        info=[
            ERROR_MESSAGE_NOTE,
            ERROR_MESSAGE_PROBLEMS_SECTION_START,
            ERROR_MESSAGE_BAD_REVISION.format(revision="55.0.8a"),
        ],
    )
    print_section_rule(c, "Subprocess error with additional info")
    error.write(baloto_io)

    import subprocess
    import shlex

    command_line = "poetry showi --top-level --latest --no-ansi"
    cmd = shlex.split(command_line)
    print_section_rule(c, "Subprocess error without additional info")
    try:
        baloto_io.set_verbosity(Verbosity.VERBOSE)
        subprocess.run(
            args=cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            check=True,
            shell=True,
        )
    except CalledProcessError as e:
        error = BalotoRuntimeError.create(
            reason="Subprocess error",
            exception=e,
            info=[
                "This is an additional info message 1",
                "This is an additional info message 2",
                "This is an additional info message 3",
                "This is an additional info message 4",
            ],
        )
        error.write(baloto_io)
    finally:
        baloto_io.set_verbosity(current_varbosity)
