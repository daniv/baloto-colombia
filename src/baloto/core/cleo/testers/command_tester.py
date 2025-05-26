from __future__ import annotations

from io import StringIO
from typing import TYPE_CHECKING

from baloto.core.cleo.io.buffered_io import BufferedIO
from baloto.core.cleo.io.inputs.argv_input import ArgvInput
from baloto.core.cleo.io.inputs.string_input import StringInput
from baloto.core.cleo.io.outputs.buffered_output import BufferedOutput


if TYPE_CHECKING:
    from baloto.core.commands.command import Command
    from baloto.core.cleo.io.outputs.output import Verbosity


class CleoCommandTester:
    """
    Eases the testing of console commands.
    """

    def __init__(self, command: Command) -> None:
        from baloto.core.rich.builders.director import RichDirector

        self._command = command
        console = RichDirector().console_builder(markup=True, highlight=True, force_terminal=True).build()
        self._io = BufferedIO(console)
        self._inputs: list[str] = []
        self._status_code: int | None = None

    @property
    def command(self) -> Command:
        return self._command

    @property
    def io(self) -> BufferedIO:
        return self._io

    @property
    def status_code(self) -> int | None:
        return self._status_code

    def execute(
            self,
            args: str = "",
            inputs: str | None = None,
            interactive: bool | None = None,
            verbosity: Verbosity | None = None,
            decorated: bool | None = None,
            supports_utf8: bool = True,
    ) -> int:
        """
        Executes the command
        """
        application = self._command.application

        io_input: StringInput | ArgvInput = StringInput(args)
        if (
                application is not None
                and application.definition.has_argument("command")
                and self._command.name is not None
        ):
            name = self._command.name
            if " " in name:
                # If the command is namespaced we rearrange
                # the input to parse it as a single argument
                argv = [application.name, self._command.name, *io_input._tokens]

                input_ = ArgvInput(argv)
            else:
                input_ = StringInput(name + " " + args)

        self._io.input = io_input
        assert isinstance(self._io.output, BufferedOutput)
        assert isinstance(self._io.error_output, BufferedOutput)

        if inputs is not None:
            self._io.input.set_stream(StringIO(inputs))

        if verbosity is not None:
            self._io.set_verbosity(verbosity)

        self._status_code = self._command.run(self._io)

        return self._status_code
