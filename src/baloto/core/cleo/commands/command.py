from __future__ import annotations

import inspect
from abc import ABC, abstractmethod

from typing import TYPE_CHECKING
from typing import Any
from typing import ClassVar
from typing import cast

from baloto.core.cleo.exceptions import CleoError

from baloto.core.cleo.io.inputs.definition import Definition
from baloto.core.cleo.io.inputs.string_input import StringInput
from baloto.core.cleo.io.null_io import NullIO
from baloto.core.cleo.io.outputs.output import Verbosity

# from baloto_com.core.cleo.ui.table_separator import TableSeparator


if TYPE_CHECKING:
    from contextlib import AbstractContextManager
    from typing import Literal
    from baloto.core.cleo.application import Application
    from baloto.core.cleo.io.inputs.argument import Argument
    from baloto.core.cleo.io.inputs.option import Option
    from baloto.core.cleo.io.io import IO

    from rich.text import Text

    # from baloto_com.core.cleo.ui.progress_bar import ProgressBar
    # from baloto_com.core.cleo.ui.progress_indicator import ProgressIndicator
    # from baloto_com.core.cleo.ui.question import Question
    # from baloto_com.core.cleo.ui.table import Rows
    # from baloto_com.core.cleo.ui.table import Table


class Command(ABC):
    arguments: ClassVar[list[Argument]] = []
    options: ClassVar[list[Option]] = []
    aliases: ClassVar[list[str]] = []
    usages: ClassVar[list[str]] = []
    commands: ClassVar[list[Command]] = []
    name: str | None = None

    description = ""

    help = ""

    enabled = True
    hidden = False

    def __init__(self) -> None:
        self._io: IO | None = None
        self._definition = Definition()
        self._full_definition: Definition | None = None
        self._application: Application | None = None
        self._ignore_validation_errors = False
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

        is_single_command = self._application and self._application.is_single_command

        if self._application:
            current_script = self._application.name
        else:
            current_script = inspect.stack()[-1][1]

        return help_text.format(
            command_name=self.name,
            command_full_name=(
                current_script if is_single_command else f"{current_script} {self.name}"
            ),
            script_name=current_script,
        )

    @property
    def application(self) -> Application | None:
        return self._application

    @application.setter
    def application(self, application: Application | None = None) -> None:
        self._application = application

        self._full_definition = None

    @property
    def ignore_validation_errors(self) -> bool:
        return self._ignore_validation_errors

    @ignore_validation_errors.setter
    def ignore_validation_errors(self, ignore: bool) -> None:
        self._ignore_validation_errors = ignore

    def configure(self) -> None:
        for argument in self.arguments:
            self._definition.add_argument(argument)

        for option in self.options:
            self._definition.add_option(option)

    def merge_application_definition(self, merge_args: bool = True) -> None:
        if self._application is None:
            return

        self._full_definition = Definition()
        self._full_definition.add_options(self._definition.options)
        self._full_definition.add_options(self._application.definition.options)

        if merge_args:
            self._full_definition.set_arguments(self._application.definition.arguments)
            self._full_definition.add_arguments(self._definition.arguments)
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

    @abstractmethod
    def interact(self, io: IO) -> None:
        """
        Interacts with the user.
        """
        raise NotImplementedError

    @abstractmethod
    def handle(self) -> int:
        """
        Execute the command.
        """
        raise NotImplementedError

    def setup(self) -> int:
        pass

    def teardown(self) -> int:
        pass

    def run(self, io: IO) -> int:
        self.merge_application_definition()

        try:
            io.input.bind(self.definition)
        except CleoError:
            if not self._ignore_validation_errors:
                raise

        if io.input.interactive:
            self.interact(io)

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
        from baloto.core.cleo.io.null_io import NullIO

        assert self.application is not None
        command = self.application.get(name)
        # noinspection PyProtectedMember
        return self.application._run_command(command, NullIO(StringInput(args or "")))

    def synopsis(self, short: bool = False) -> str | Text:
        key = "short" if short else "long"

        if key not in self._synopsis:
            self._synopsis[key] = (
                f"[repr.call]{self.name}[/repr.call] {self.definition.synopsis(short)}"
            )

        return self._synopsis[key]



