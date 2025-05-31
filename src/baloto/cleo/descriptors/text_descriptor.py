from __future__ import annotations

import re
from typing import Any
from typing import TYPE_CHECKING

from rich.panel import Panel
from rich.table import Table, Column
from rich.text import Text

from baloto.cleo.commands.cleo_command import Command
from baloto.cleo.descriptors.application_descriptor import ApplicationDescription
from baloto.cleo.descriptors.descriptor import Descriptor
from baloto.cleo.io.inputs.definition import Definition

if TYPE_CHECKING:
    from baloto.cleo.cleo_application import Application
    from baloto.cleo.io.inputs.argument import Argument
    from baloto.cleo.io.inputs.option import Option
    from rich.console import RenderableType


class TextDescriptor(Descriptor):

    def _describe_argument(self, argument: Argument, **options: Any) -> list[RenderableType]:

        if argument.default is not None and (
            not isinstance(argument.default, list) or argument.default
        ):
            formatted = _format_default_value(argument.default)
            default = f"[comment](default = {formatted})[/]"
        else:
            default = ""

        if argument.choices:
            choices = (
                f"[comment] {{{_format_choices(argument.choices)}}}[/]"
            )
        else:
            choices = ""

        total_width = options.get("total_width", len(argument.name))

        sub_argument_description = re.sub(
            r"\s*[\r\n]\s*",
            "\n" + " " * (total_width + 4),
            argument.description,
        )

        argument_name = Text(argument.name, style="argument")
        return [argument_name, sub_argument_description, f"[inspect.attr]{default}[/]", choices]

    def _describe_option(self, option: Option, **options: Any) -> list[RenderableType]:
        if (
            option.accepts_value
            and option.default is not None
            and (not isinstance(option.default, list) or option.default)
        ):
            formatted = _format_default_value(option.default)
            default = f"(default = {formatted})"
        else:
            default = ""

        value = ""
        if option.accepts_value:
            value = "=" + option.name.upper()

            if not option.is_value_required():
                value = "[" + value + "]"

        total_width = options.get("total_width", _calculate_total_width_for_options([option]))
        option_shortcut = (
            Text(f"-{option.shortcut}", style="switch") if option.shortcut else Text("")
        )
        synopsis = Text(f"--{option.name} ", style="switch").append(value, style="bold dim")

        sub_option_description = re.sub(
            r"\s*[\r\n]\s*",
            "\n" + " " * (total_width + 4),
            option.description,
        )
        are_multiple_values_allowed = (
            "[dim](multiple values allowed)[/]" if option.is_list else ""
        )
        are_choices_allowed = (
            f"[comment] {{{', '.join(option.choices)}}}[/comment]"
            if option.choices
            else ""
        )
        sub_option_description = (
            f"{sub_option_description} "
            f"[inspect.attr]{default}[/] {are_multiple_values_allowed} {are_choices_allowed}"
        )

        return [option_shortcut, synopsis, sub_option_description]

    def _describe_definition(self, definition: Definition, **options: Any) -> None:

        def get_table() -> Table:
            return Table(
                Column(header="switch", style="switch"),
                Column(header="option", style="switch"),
                highlight=True, box=None, show_header=False
            )

        def get_panel(table: Table, title: str) -> Panel:
            if command:
                return Panel(table, border_style="dim", title=title, title_align="left")
            else:
                return Panel(table, border_style="dim", title=title, title_align="left")

        command: Command | None = options.get("command", None)
        arguments = definition.arguments()
        if arguments:
            arguments_table = get_table()
            for argument in arguments:
                renderable = self._describe_argument(argument)
                arguments_table.add_row(*renderable)

            panel = get_panel(arguments_table, "Arguments")
            self._io.output.write(panel)

        definition_options = definition.options
        if definition_options:
            options_table = get_table()
            later_options = []

            for option in definition_options():
                if option.shortcut and len(option.shortcut) > 1:
                    later_options.append(option)
                    continue

                renderable = self._describe_option(option)
                options_table.add_row(*renderable)

            for option in later_options:
                renderable = self._describe_option(option)
                options_table.add_row(*renderable)

            panel = get_panel(options_table, "Options")
            self._io.output.write(panel)

    def _describe_command(self, command: Command, **options: Any) -> None:

        description = command.description
        if description:
            self._io.output.write(f"[dark_orange]Description:[/] {description}", end="\n\n")

        command.merge_application_definition(False)

        for usage in [command.synopsis(True), *command.aliases, *command.usages]:
            self._io.output.write("[dark_orange]Usage:[/]", end=" ", new_line_start=False)
            self._io.output.write(usage, new_line_start=False)

        if command.definition.options or command.definition.arguments:
            self._io.output.write("", end="\n")
            self._describe_definition(command.definition, **options, command=command)

        help_text = command.processed_help
        if help_text and help_text != description:
            help_text = help_text.replace("\n", "\n  ")

            self._io.output.write(
                Panel(
                    help_text, highlight=True, border_style="dim", title="Help", title_align="left"
                ),
                end="\n",
            )

    def _describe_application(self, application: Application, **options: Any) -> None:

        self._io.output.write(
            application.help,
            "\n\n",
            f"[dim]{application.description.upper()}[/]",
            justify="center",
        )
        self._io.output.write("", end="\n\n")
        if options.get("title", False):
            return

        described_namespace = options.get("namespace")
        description = ApplicationDescription(application, namespace=described_namespace)

        self._io.output.write(
            "[dark_orange]Usage:[/] command \\[options] \\[arguments]", justify="left"
        )
        self._io.output.write("", end="\n")
        self._describe_definition(Definition(application.definition.options()), **options)

        commands = description.commands
        namespaces = description.namespaces

        if described_namespace and namespaces:
            described_namespace_info = next(iter(namespaces.values()))
            for name in described_namespace_info["commands"]:
                commands[name] = description.command(name)

        all_commands = list(commands)
        for namespace in namespaces.values():
            all_commands += namespace["commands"]

        if described_namespace:
            title = f"Available commands for the '{described_namespace}' namespace"
        else:
            title = "Available commands"

        for namespace in namespaces.values():
            namespace["commands"] = [c for c in namespace["commands"] if c in commands]

            if not namespace["commands"]:
                continue

            if not (
                described_namespace or namespace["id"] == ApplicationDescription.GLOBAL_NAMESPACE
            ):
                title = f"[command]{namespace['id']}[/]"

            table = Table(
                Column(header="cmd", style="command"),
                Column(header="aliases", style="alias"),
                highlight=True, box=None, show_header=False
            )
            for name in namespace["commands"]:
                command = commands[name]
                command_aliases = _get_command_aliases_text(command) if command.name == name else ""
                table.add_row(name, command_aliases, command.description)

            panel = Panel(table, border_style="dim", title=title, title_align="left")

            self._io.output.write(panel)


def _format_default_value(default: Any) -> str:
    import json
    from baloto.core.cleo.utils import escape

    if isinstance(default, str):
        default = escape(default)
    elif isinstance(default, list):
        default_str = [escape(value) for value in default if isinstance(value, str)]
        default_int = [value for value in default if isinstance(value, int)]
        default_float = [value for value in default if isinstance(value, float)]
        default = default_str + default_int + default_float
    elif isinstance(default, dict):
        default = {
            key: escape(value) for key, value in default.items() if isinstance(value, str)
        }

    return json.dumps(default).replace("\\\\", "\\")

def _format_choices(choices: list[str]) -> str:
    return ", ".join(choices)

def _calculate_total_width_for_options(options: list[Option]) -> int:
    total_width = 0

    for option in options:
        name_length = 1 + max(len(option.shortcut or ""), 1) + 4 + len(option.name)

        if option.accepts_value:
            value_length = 1 + len(option.name)
            if not option.is_value_required():
                value_length += 2

            name_length += value_length

        total_width = max(total_width, name_length)

    return total_width


def _get_command_aliases_text(command: Command) -> str:
    aliases = command.aliases

    if aliases:
        return f"\\[{ '|'.join(aliases) }] "

    return ""
