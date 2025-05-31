from __future__ import annotations

import sys
from collections.abc import Sequence
from typing import Any

from baloto.cleo.exceptions.errors import CleoLogicError
from baloto.cleo.io.inputs.argument import Argument
from baloto.cleo.io.inputs.option import Option


# class Definition:
#     """
#     A Definition represents a set of command line arguments and options.
#     """
#
#     def __init__(self, definition: Sequence[Argument | Option] | None = None) -> None:
#
#         self._arguments: dict[str, Argument] = dict()
#         self._options: dict[str, Option] = dict()
#         self._shortcuts: dict[str, str] = dict()
#         self._required_count = 0
#         self._has_list_argument = False
#         self._has_optional = False
#
#         self.set_definition(definition or list())
#
#     # @property
#     # def arguments(self) -> list[Argument]:
#     #     return list(self._arguments.values())
#
#     # @property
#     def arguments(self) -> Iterator[Argument]:
#         return iter(self._arguments.values())
#
#     @property
#     def argument_count(self) -> int:
#         if self._has_list_argument:
#             return sys.maxsize
#
#         return len(self._arguments)
#
#     @property
#     def required_argument_count(self) -> int:
#         return self._required_count
#
#     @property
#     def argument_defaults(self) -> dict[str, Any]:
#         values = {}
#
#         for argument in self._arguments.values():
#             values[argument.name] = argument.default
#
#         return values
#
#     # @property
#     # def options(self) -> list[Option]:
#     #     return list(self._options.values())
#
#     def options(self) -> Iterator[Option]:
#         return iter(self._options.values())
#
#     @property
#     def option_defaults(self) -> dict[str, Any]:
#         return {o.name: o.default for o in self._options.values()}
#
#     def set_definition(self, definition: Sequence[Argument | Option]) -> None:
#         arguments_list: list[Argument] = []
#         options_list: list[Option] = []
#
#         if definition:
#             for item in definition:
#                 if isinstance(item, Option):
#                     options_list.append(item)
#                 else:
#                     arguments_list.append(item)
#
#             self.set_arguments(arguments_list)
#             self.set_options(options_list)
#
#     def set_arguments(self, arguments: list[Argument]) -> None:
#         self._arguments = dict()
#         self._required_count = 0
#         self._has_list_argument = False
#         self._has_optional = False
#         self.add_arguments(arguments)
#
#     def add_arguments(self, arguments: list[Argument]) -> None:
#         for argument in arguments:
#             self.add_argument(argument)
#
#     def add_argument(self, argument: Argument) -> None:
#         if argument.name in self._arguments:
#             raise CleoLogicError(f'An argument with name "{argument.name}" already exists', code="arg-already-exists")
#
#         if self._has_list_argument:
#             raise CleoLogicError("Cannot add an argument after a list argument", code="arg-after-list-arg")
#
#         try:
#             if argument.required and self._has_optional:
#                 raise CleoLogicError("Cannot add a required argument after an optional one", code="arg-after-opyional-arg")
#         except Exception as e:
#             i = 0
#
#         if argument.is_list:
#             self._has_list_argument = True
#
#         if argument.required:
#             self._required_count += 1
#         else:
#             self._has_optional = True
#
#         self._arguments[argument.name] = argument
#
#     def argument(self, name: str | int) -> Argument:
#         if not self.has_argument(name):
#             raise ValueError(f'The "{name}" argument does not exist')
#
#         if isinstance(name, int):
#             arguments = list(self._arguments.values())
#             return arguments[name]
#
#         return self._arguments[name]
#
#     def has_argument(self, name: str | int) -> bool:
#         if isinstance(name, int):
#             # Check if this is a valid argument index
#             # abs(x + (x < 0)) to normalize negative indices
#             return abs(name + (name < 0)) < len(self._arguments)
#         return name in self._arguments
#
#     def set_options(self, options: list[Option]) -> None:
#         self._options = dict()
#         self._shortcuts = dict()
#         self.add_options(options)
#
#     def add_options(self, options: list[Option]) -> None:
#         for option in options:
#             self.add_option(option)
#
#     def add_option(self, option: Option) -> None:
#         if option.name in self._options and option != self._options[option.name]:
#             raise CleoLogicError(f'An option named "{option.name}" already exists')
#
#         if option.shortcut:
#             for shortcut in option.shortcut.split("|"):
#                 if shortcut in self._shortcuts and option.name != self._shortcuts[shortcut]:
#                     raise CleoLogicError(f'An option with shortcut "{shortcut}" already exists')
#
#         self._options[option.name] = option
#
#         if option.shortcut:
#             for shortcut in option.shortcut.split("|"):
#                 self._shortcuts[shortcut] = option.name
#
#     def option(self, name: str) -> Option:
#         if not self.has_option(name):
#             raise ValueError(f'The option "--{name}" option does not exist')
#
#         return self._options[name]
#
#     def has_option(self, name: str) -> bool:
#         return name in self._options
#
#     def has_shortcut(self, shortcut: str) -> bool:
#         return shortcut in self._shortcuts
#
#     def option_for_shortcut(self, shortcut: str) -> Option:
#         return self._options[self.shortcut_to_name(shortcut)]
#
#     def shortcut_to_name(self, shortcut: str) -> str:
#         if shortcut not in self._shortcuts:
#             raise ValueError(f'The "-{shortcut}" option does not exist')
#
#         return self._shortcuts[shortcut]
#
#     def synopsis(self, short: bool = False) -> str:
#         elements = []
#
#         if short and self._options:
#             elements.append("[options]")
#         elif not short:
#             for option in self._options.values():
#                 value = ""
#                 if option.accepts_value:
#                     formatted = option.name.upper() if option.requires_value else f"[{option.name.upper()}]"
#                     value = f" {formatted}"
#
#                 shortcut = ""
#                 if option.shortcut:
#                     shortcut = f"-{option.shortcut}|"
#
#                 elements.append(f"[{shortcut}--{option.name}{value}]")
#
#         if elements and self._arguments:
#             elements.append("[--]")
#
#         tail = ""
#         for argument in self._arguments.values():
#             element = f"<{argument.name}>"
#             if argument.is_list:
#                 element += "..."
#
#             if not argument.required:
#                 element = "[" + element
#                 tail += "]"
#
#             elements.append(element)
#
#         return " ".join(elements) + tail

class Definition:
    """
    A Definition represents a set of command line arguments and options.
    """

    def __init__(self, definition: Sequence[Argument | Option] | None = None) -> None:
        self._arguments: dict[str, Argument] = {}
        self._required_count = 0
        self._has_list_argument = False
        self._has_optional = False
        self._options: dict[str, Option] = {}
        self._shortcuts: dict[str, str] = {}

        self.set_definition(definition or [])

    def arguments(self) -> list[Argument]:
        return list(self._arguments.values())

    @property
    def argument_count(self) -> int:
        if self._has_list_argument:
            return sys.maxsize

        return len(self._arguments)

    @property
    def required_argument_count(self) -> int:
        return self._required_count

    @property
    def argument_defaults(self) -> dict[str, Any]:
        values = {}

        for argument in self._arguments.values():
            values[argument.name] = argument.default

        return values

    def options(self) -> list[Option]:
        return list(self._options.values())

    @property
    def option_defaults(self) -> dict[str, Any]:
        return {o.name: o.default for o in self._options.values()}

    def set_definition(self, definition: Sequence[Argument | Option]) -> None:
        arguments = []
        options = []

        if definition:
            for item in definition:
                if isinstance(item, Option):
                    options.append(item)
                else:
                    arguments.append(item)

            self.set_arguments(arguments)
            self.set_options(options)

    def set_arguments(self, arguments: list[Argument]) -> None:
        self._arguments = {}
        self._required_count = 0
        self._has_list_argument = False
        self._has_optional = False
        self.add_arguments(arguments)

    def add_arguments(self, arguments: list[Argument]) -> None:
        for argument in arguments:
            self.add_argument(argument)

    def add_argument(self, argument: Argument) -> None:
        if argument.name in self._arguments:
            raise CleoLogicError(
                f'An argument with name "{argument.name}" already exists', code=""
            )

        if self._has_list_argument:
            raise CleoLogicError("Cannot add an argument after a list argument")

        if argument.required and self._has_optional:
            raise CleoLogicError("Cannot add a required argument after an optional one", code="")

        if argument.is_list:
            self._has_list_argument = True

        if argument.required:
            self._required_count += 1
        else:
            self._has_optional = True

        self._arguments[argument.name] = argument

    def argument(self, name: str | int) -> Argument:
        if not self.has_argument(name):
            raise ValueError(f'The "{name}" argument does not exist')

        if isinstance(name, int):
            arguments = list(self._arguments.values())
            return arguments[name]

        return self._arguments[name]

    def has_argument(self, name: str | int) -> bool:
        if isinstance(name, int):
            # Check if this is a valid argument index
            # abs(x + (x < 0)) to normalize negative indices
            return abs(name + (name < 0)) < len(self._arguments)
        return name in self._arguments

    def set_options(self, options: list[Option]) -> None:
        self._options = {}
        self._shortcuts = {}
        self.add_options(options)

    def add_options(self, options: list[Option]) -> None:
        for option in options:
            self.add_option(option)

    def add_option(self, option: Option) -> None:
        if option.name in self._options and option != self._options[option.name]:
            raise CleoLogicError(f'An option named "{option.name}" already exists', code="")

        if option.shortcut:
            for shortcut in option.shortcut.split("|"):
                if (
                    shortcut in self._shortcuts
                    and option.name != self._shortcuts[shortcut]
                ):
                    raise CleoLogicError(
                        f'An option with shortcut "{shortcut}" already exists', code=""
                    )

        self._options[option.name] = option

        if option.shortcut:
            for shortcut in option.shortcut.split("|"):
                self._shortcuts[shortcut] = option.name

    def option(self, name: str) -> Option:
        if not self.has_option(name):
            raise ValueError(f'The option "--{name}" option does not exist')

        return self._options[name]

    def has_option(self, name: str) -> bool:
        return name in self._options

    def has_shortcut(self, shortcut: str) -> bool:
        return shortcut in self._shortcuts

    def option_for_shortcut(self, shortcut: str) -> Option:
        return self._options[self.shortcut_to_name(shortcut)]

    def shortcut_to_name(self, shortcut: str) -> str:
        if shortcut not in self._shortcuts:
            raise ValueError(f'The "-{shortcut}" option does not exist')

        return self._shortcuts[shortcut]

    def synopsis(self, short: bool = False) -> str:
        elements = []

        if short and self._options:
            elements.append("[options]")
        elif not short:
            for option in self._options.values():
                value = ""
                if option.accepts_value:
                    formatted = (
                        option.name.upper()
                        if option.is_value_required()
                        else f"[{option.name.upper()}]"
                    )
                    value = f" {formatted}"

                shortcut = ""
                if option.shortcut:
                    shortcut = f"-{option.shortcut}|"

                elements.append(f"[{shortcut}--{option.name}{value}]")

        if elements and self._arguments:
            elements.append("[--]")

        tail = ""
        for argument in self._arguments.values():
            element = f"<{argument.name}>"
            if argument.is_list:
                element += "..."

            if not argument.required:
                element = "[" + element
                tail += "]"

            elements.append(element)

        return " ".join(elements) + tail

