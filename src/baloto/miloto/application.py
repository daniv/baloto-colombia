from __future__ import annotations


from baloto.core.application import Application as CoreApplication
from baloto.core.loaders.command_loader import CommandLoader
from baloto.core.loaders.command_loader import load_command
from baloto.core.__version__ import __version__


COMMANDS = [
]

class Application(CoreApplication):
    def __init__(self):
        super().__init__("miloto", __version__)
        from baloto.core.commands.about import AboutCommand

        about = AboutCommand()
        about.caller = "miloto"
        self.add(about)

        command_loader = CommandLoader(
            {name: load_command("baloto.miloto.commands.", name) for name in COMMANDS}
        )
        self.set_command_loader(command_loader)

    @property
    def command_loader(self) -> CommandLoader:
        command_loader = self._command_loader
        assert isinstance(command_loader, CommandLoader)
        return command_loader



def main() -> int:
    exit_code: int = Application().run()
    return exit_code


if __name__ == "__main__":
    main()
