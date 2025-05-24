from __future__ import annotations

from typing import Any
from typing import TYPE_CHECKING

import pytest

from baloto.core.config.config_source import UNSET
from baloto.core.config.dict_config_source import DictConfigSource
from baloto.core.utils.console_message import ConsoleMessage
from tests.utils import print_section_rule

if TYPE_CHECKING:
    from baloto.core.cleo.io.outputs.console_output import ConsoleOutput
    from baloto.core.cleo.io.io import IO


@pytest.fixture(scope="module", name="config_source")
def dict_config() -> DictConfigSource:
    source = DictConfigSource()
    source.add_property("key1", "value1")
    source.add_property("key2", 4)
    source.add_property("key3", 3.14)
    source.add_property("key4", False)
    source.add_property("key5", [1, 2, 3])
    source.add_property("key6", {})
    source.add_property("key6.sub_key1", "sub_value1")
    source.add_property("key6.sub_key2", 5)
    source.add_property("key6.sub_key3", 3.15)
    source.add_property("key6.sub_key4", True)

    yield source

    source.config.clear()


WARN_MSG = "[warning][b]WARNING[/]: No build backend defined. Please define one in the [c1]pyproject.toml[/].\n"
"Falling back to using the built-in 'poetry-core' version.\n"
"In a future release Poetry will fallback to 'setuptools' as defined by PEP 517.\n"
"More details can be found at https://python-poetry.org/docs/libraries/#packaging[/]"


@pytest.mark.parametrize(
    "new_key, new_value", [(None, 77), ("key6.sub_key4", "SSS"), ("key5", UNSET), ("key1", 1_000)]
)
def message_dump_test(
    console_output: ConsoleOutput, config_source: DictConfigSource, new_key: str, new_value: Any
) -> None:
    import json

    c = console_output.console
    c.line()

    from rich.json import JSON

    # console.log(JSON('["foo", "bar"]'))

    old_key = new_key or "key3"
    print_section_rule(c, "Message with dump text")
    old_value = config_source.get_property(old_key)
    msg = f"[c1]{old_key}[/c1] = [c2]{json.dumps(old_value)}[/c2]"

    if new_key is not None and new_value is not UNSET:
        msg += f" -> [c1]{new_key}[/c1] = [c2]{json.dumps(new_value)}[/c2]"
        config_source.add_property(new_key, new_value)
    elif new_key is None:
        msg += " -> [c1]Removed from config[/c1]"
        config_source.remove_property(old_key)
    elif new_key and new_value is UNSET:
        msg += f" -> [c1]{new_key}[/c1] = [c2]Not explicit set[/c2]"

    console_output.write(msg)


def warning_message_test(baloto_io: IO):
    c = getattr(baloto_io.output, "console")
    c.line()

    print_section_rule(c, "Message with dump text")
    baloto_io.write_error(
        "[warning][b]WARNING[/]: No build backend defined. Please define one in the [c1]pyproject.toml[/].\n"
        "Falling back to using the built-in 'poetry-core' version.\n"
        "In a future release Poetry will fallback to 'setuptools' as defined by PEP 517.\n"
        "More details can be found at https://python-poetry.org/docs/libraries/#packaging[/]"
    )

    print_section_rule(c, "Message with tags")
    baloto_io.write_error(
        f"[warning]'--local-version' is deprecated."
        f" Use '[yellow]--config-settings local-version=1.4.5[/]'"
        f" instead.[/warning]"
    )


def message_test(baloto_io: IO):
    c = getattr(baloto_io.output, "console")
    c.print("Caca ba leben")
    c.line()

    print_section_rule(c, "Test with multi line and section title")
    message = ConsoleMessage("Multi-line\nText")
    actual = message.make_section("Title", indent=">>>").text
    baloto_io.output.write(actual)

    print_section_rule(c, "Test with empty test and section title")
    message = ConsoleMessage("This is a simple note")
    text = message.make_section("[violet]Note[/]", indent=" - ").text
    baloto_io.output.write(text)

    print_section_rule(c, "More_message")
    strings_list = ["python", "java", "C#", "Javascript", "Typescript", "Html"]
    messages = [
        ConsoleMessage(
            "The following wheel(s) were skipped as the current project environment does not support them "
            "due to abi compatibility issues.",
            debug=True,
        ),
        ConsoleMessage("\n".join(strings_list), debug=True).indent("  - ").wrap("warning"),
        ConsoleMessage(
            "If you would like to see the supported tags in your project environment, you can execute "
            "the following command:\n"
            "    [c1]poetry debug tags[/]",
            debug=True,
        ),
    ]

    for message in messages:
        baloto_io.output.write(message.text)
