from __future__ import annotations

from io import StringIO
from typing import TYPE_CHECKING

from baloto.core.cleo.io.buffered_io import BufferedIO
from baloto.core.cleo.io.inputs.string_input import StringInput
from baloto.core.cleo.io.outputs.buffered_output import BufferedOutput
from baloto.core.rich.builders.director import RichDirector

if TYPE_CHECKING:
    from baloto.core.cleo.application import Application
    from baloto.core.cleo.io.outputs.output import Verbosity


class CleoApplicationTester:
    """
    Eases the testing of console applications.
    """

    def __init__(self, application: Application) -> None:
        self._application = application
        self._application.auto_exit = False
        console = RichDirector().console_builder(markup=True, highlight=True, force_terminal=True).build()
        self._io = BufferedIO(console)
        self._status_code = 0

    @property
    def application(self) -> Application:
        return self._application

    @property
    def io(self) -> BufferedIO:
        return self._io

    @property
    def status_code(self) -> int:
        return self._status_code

    def execute(
            self,
            args: str = "",
            inputs: str | None = None,
            interactive: bool = True,
            verbosity: Verbosity | None = None,
    ) -> int:
        """
        Executes the command
        """
        self._io.clear()

        self._io.input = StringInput(args)
        assert isinstance(self._io.output, BufferedOutput)
        assert isinstance(self._io.error_output, BufferedOutput)

        if inputs is not None:
            self._io.input = StringIO(inputs)

        if verbosity is not None:
            self._io.set_verbosity(verbosity)

        self._status_code = self._application.run(
            self._io.input,
            self._io.output,
            self._io.error_output,
        )

        return self._status_code
