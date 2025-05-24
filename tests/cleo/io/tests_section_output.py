from __future__ import annotations

import time
import typing
from typing import TYPE_CHECKING

import pytest

from baloto.core.cleo.io.outputs.section_output import SectionOutput

if TYPE_CHECKING:
    from rich.console import Console
    from baloto.core.cleo.io.outputs.console_output import ConsoleOutput
    from baloto.core.cleo.io.io import IO


@pytest.fixture(scope="module")
def stream(console: Console) -> typing.IO[str]:
    return console.file


@pytest.fixture(scope="module")
def sections() -> list[SectionOutput]:
    return []


@pytest.fixture(scope="module", name="section")
def output(console: Console, sections: list[SectionOutput]) -> SectionOutput:
    return SectionOutput(console, sections)


@pytest.fixture(scope="module", name="baloto_io")
def baloto_io(console_output: ConsoleOutput, error_console_output: ConsoleOutput):
    from baloto.core.cleo.io.inputs.argv_input import ArgvInput
    from baloto.core.cleo.io.io import IO
    import sys

    input = ArgvInput()
    input.stream = sys.stdin
    output = console_output
    error_output = error_console_output

    return IO(input, output, error_output)


@pytest.fixture(scope="module")
def cleo_io():
    import sys
    from cleo.io.inputs.argv_input import ArgvInput
    from cleo.io.outputs.stream_output import StreamOutput
    from cleo.io.io import IO

    input = ArgvInput()
    input.set_stream(sys.stdin)

    output = StreamOutput(sys.stdout)

    error_output = StreamOutput(sys.stderr)

    return IO(input, output, error_output)


def clear_all_test(output: SectionOutput) -> None:
    output.write("Foo\nBar")
    output.clear()


def test_clear_with_number_of_lines_and_multiple_sections_test(
    output: SectionOutput, console: Console
) -> None:
    console.line()

    output.write("Foo")
    output.write("[red]Bar[/]")
    time.sleep(2)
    output.clear(1)
    output.write("[blue]Baz[/]")


def test_overwrite_multiple_lines_test(output: SectionOutput, console: Console) -> None:
    console.line()
    output.write("Foo\nBar\nBaz")
    output.overwrite("Bar")


def executor_test(baloto_io: IO):
    op_message = "Te extraño un monton mi bolti te quiero conmigo"
    section = baloto_io.section()
    baloto_io.output.write("")
    section.write("Mi mayor dolor")
    section.write(f"  [blue bold]-[/] {op_message}:" " [blue]Pending...[/]", end="")
    section.clear()
    skip_reason = "Te fuiste al cielo"
    section.write(
        f"  [blue bold]-[/] {op_message}: "
        "[yellow bold]Skipped[/] "
        "[c2]for the following reason:[/] "
        f"[c2]{skip_reason}[/]",
    )
