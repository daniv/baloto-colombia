from __future__ import annotations

import inspect
from abc import ABC, abstractmethod
from typing import Any
from typing import ClassVar
from typing import TYPE_CHECKING

from baloto.cleo.exceptions.errors import CleoError
from baloto.cleo.io.inputs.definition import Definition
from baloto.cleo.io.inputs.string_input import StringInput
from baloto.cleo.io.outputs.output import Verbosity

if TYPE_CHECKING:
    from baloto.cleo.cleo_application import Application
    from baloto.cleo.io.inputs.argument import Argument
    from baloto.cleo.io.inputs.option import Option
    from baloto.cleo.io.io import IO
    from rich.text import Text
    from rich.text import TextType
    from rich.style import Style
    from rich.console import JustifyMethod
    from rich.console import OverflowMethod
    from rich.align import AlignMethod

    # from baloto.poetry.poetry import Poetry


class Command(ABC):
    name: str | None = None
    description: str = ""
    help: str = ""
    enabled: bool = True
    hidden: bool = False
    style: str = "command"

    aliases: ClassVar[list[str]] = []
    arguments: ClassVar[list[Argument]] = []
    options: ClassVar[list[Option]] = []
    usages: ClassVar[list[str]] = []
    commands: ClassVar[list[Command]] = []

    def __init__(self) -> None:
        self.ignore_validation_errors = False

        self._io: IO | None = None
        # self._poetry: Poetry | None = None
        self._definition = Definition()
        self._full_definition: Definition | None = None
        self.application: Application | None = None

        self._synopsis: dict[str, str] = {}

        self.configure()

        for i, usage in enumerate(self.usages):
            if self.name and not usage.startswith(self.name):
                self.usages[i] = f"{self.name} {usage}"

    @property
    def io(self) -> IO:
        return self._io

    @property
    def definition(self) -> Definition:
        if self._full_definition is not None:
            return self._full_definition

        return self._definition

    @property
    def processed_help(self) -> str:
        help_text = self.help
        if not self.help:
            help_text = self.description

        is_single_command = self._application and self._application.single_command

        if self._application:
            current_script = self._application.name
        else:
            current_script = inspect.stack()[-1][1]

        return help_text.format(
            command_name=self.name,
            command_full_name=(current_script if is_single_command else f"{current_script} {self.name}"),
            script_name=current_script,
        )

    @property
    def application(self) -> Application | None:
        return self._application

    @application.setter
    def application(self, application: Application | None = None) -> None:
        self._application = application

        self._full_definition = None

    def merge_application_definition(self, merge_args: bool = True) -> None:
        if self._application is None:
            return

        self._full_definition = Definition()
        self._full_definition.add_options(list(self._definition.options()))
        self._full_definition.add_options(list(self._application.definition.options()))

        if merge_args:
            self._full_definition.set_arguments(list(self._application.definition.arguments()))
            self._full_definition.add_arguments(list(self._definition.arguments()))
        else:
            self._full_definition.set_arguments(self._definition.arguments)

    def argument(self, name: str) -> Any:
        """
        Get the value of a command argument.
        """
        return self._io.input.argument(name)

    def option(self, name: str) -> Any:
        """
        Get the value of a command option.
        """
        return self._io.input.option(name)

    def configure(self) -> None:
        for argument in self.arguments:
            self._definition.add_argument(argument)

        for option in self.options:
            self._definition.add_option(option)

    @abstractmethod
    def handle(self) -> int:
        """
        Execute the command.
        """
        raise NotImplementedError

    def initialize(self, io: IO) -> None:
        pass

    def setup(self) -> int:
        pass

    def teardown(self) -> int:
        pass

    def run(self, io: IO) -> int:
        self.merge_application_definition()

        try:
            io.input.bind(self.definition)
        except CleoError:
            if not self.ignore_validation_errors:
                raise

        if io.input.has_argument("command") and io.input.argument("command") is None:
            io.input.set_argument("command", self.name)

        io.input.validate()

        return self.execute(io) or 0

    def execute(self, io: IO) -> int:
        self._io = io

        try:
            exit_code = self.setup() or 0
            if exit_code:
                return exit_code

            exit_code = self.handle() or 0
            if exit_code:
                return exit_code

            return self.teardown()

        except KeyboardInterrupt:
            return 1

    def call(self, name: str, args: str | None = None) -> int:
        assert self.application is not None
        command = self.application.get(name)

        # noinspection PyProtectedMember
        return self.application._run_command(command, self._io.with_input(StringInput(args or "")))

    def call_silent(self, name: str, args: str | None = None) -> int:
        """
        Call another command silently.

        :param name: The command name
        :param args: arguments
        :return: return code
        """
        from baloto.cleo.io.null_io import NullIO

        assert self.application is not None
        command = self.application.get(name)
        # noinspection PyProtectedMember
        return self.application._run_command(command, NullIO(StringInput(args or "")))

    def synopsis(self, short: bool = False) -> str | Text:
        key = "short" if short else "long"

        if key not in self._synopsis:
            self._synopsis[key] = f"[repr.call]{self.name}[/repr.call] {self.definition.synopsis(short)}"

        return self._synopsis[key]

    def write(
        self,
        *objects: Any,
        sep: str = " ",
        end: str = "\n",
        style: str | Style | None = None,
        justify: JustifyMethod | None = None,
        overflow: OverflowMethod | None = None,
        no_wrap: bool | None = None,
        markup: bool | None = None,
        highlight: bool = True,
        width: int | None = None,
        height: int | None = None,
        crop: bool = True,
        soft_wrap: bool | None = None,
        new_line_start: bool = False,
        verbosity: Verbosity = Verbosity.NORMAL,
    ) -> None:
        self._io.output.write(
            *objects,
            sep=sep,
            end=end,
            justify=justify,
            overflow=overflow,
            style=style,
            no_wrap=no_wrap,
            markup=markup,
            highlight=highlight,
            width=width,
            height=height,
            crop=crop,
            soft_wrap=soft_wrap,
            new_line_start=new_line_start,
            verbosity=verbosity,
        )

    def write_error(
        self,
        *objects: Any,
        sep: str = " ",
        end: str = "\n",
        style: str | Style | None = None,
        justify: JustifyMethod | None = None,
        overflow: OverflowMethod | None = None,
        no_wrap: bool | None = None,
        markup: bool | None = None,
        highlight: bool = True,
        width: int | None = None,
        height: int | None = None,
        crop: bool = True,
        soft_wrap: bool | None = None,
        new_line_start: bool = False,
        verbosity: Verbosity = Verbosity.NORMAL,
    ) -> None:
        self._io.error_output.write(
            *objects,
            sep=sep,
            end=end,
            justify=justify,
            overflow=overflow,
            style=style,
            no_wrap=no_wrap,
            markup=markup,
            highlight=highlight,
            width=width,
            height=height,
            crop=crop,
            soft_wrap=soft_wrap,
            new_line_start=new_line_start,
            verbosity=verbosity,
        )

    def lines(self, count: int = 1) -> None:
        if hasattr(self._io.output, "console"):
            self._io.output.console.lines(count)

    def rule(
        self,
        title: TextType = "",
        *,
        characters: str = "─",
        style: str | Style = "rule.line",
        align: AlignMethod = "center",
    ) -> None:
        if hasattr(self._io.output, "console"):
            self._io.output.console.rule(title, characters=characters, style=style, align=align)

    def info(self, text: str) -> None:
        """
        Write a string as information output.

        :param text: The line to write
        :type text: str
        """
        self.write(text, style="info")

    def comment(self, text: str) -> None:
        """
        Write a string as comment output.

        :param text: The line to write
        :type text: str
        """
        self.write(text, "comment")

    def question(self, text: str) -> None:
        """
        Write a string as question output.

        :param text: The line to write
        :type text: str
        """
        self.write(text, "question")

    def overwrite(self, text: str) -> None:
        """
        Overwrites the current line.

        It will not add a new line so use line('')
        if necessary.
        """
        pass
