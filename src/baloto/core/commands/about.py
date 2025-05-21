from __future__ import annotations

from baloto.core.commands.command import Command as BalotoCommand
from baloto.core.poetry.poetry import Poetry
from baloto.core.exceptions import BalotoRuntimeError


class AboutCommand(BalotoCommand):
    caller = "miloto"

    name = "about"

    description = "Shows information about [prog]Miloto[/] application."

    def handle(self) -> int:
        from rich.padding import Padding
        import platform

        app = self.get_application()
        console = self.io.console
        poetry = app.poetry
        py_version = platform.python_version()

        try:
            top_levels = poetry.get_top_levels()
        except BalotoRuntimeError as e:
            self.io.error_console.line()
            e.write(self.io)
            self.io.error_console.line()
            return e.exit_code

        console.line()
        console.print(f"¿QUE ES {self.caller.upper()}?", style="bold")
        if self.caller == "miloto":
            padding = Padding(self._get_what_is_miloto(poetry), (0, 0, 0, 2))
        else:
            padding = Padding(self._get_what_is_baloto(poetry), (0, 0, 0, 2))

        console.print(padding, new_line_start=True)
        console.print(f"Version de [prog]Baloto Project[/]: [repr.number]{app.version}[/]")
        console.print(f"Version de [prog]Python[/]        : [repr.number]{py_version}[/]")
        console.line()
        console.print("PAQUETES INSTALADOS:", style="bold", new_line_start=True)
        from rich.table import Table

        from rich import box

        table = Table(
            box=box.SIMPLE_HEAD,
            show_header=True, show_edge=False, show_lines=False
        )
        table.add_column("Package", style="prog", width=20)
        table.add_column("Version", style="repr.number", width=10)
        table.add_column("Última version", width=10)
        table.add_column("Grupos", style="bold", width=10)
        table.add_column("Descripción", width=90, overflow="fold")

        for tl in top_levels:
            lt = f"[{{tag}}]{tl.get("latest")}[/]"
            latest = lt.format(tag="green") if tl.get("version") == tl.get("latest") else lt.format(tag="yellow")
            table.add_row(
                 tl.get("name"), tl.get("version"), latest,
                ", ".join(tl.get("groups")), tl.get("description")
            )
        padding = Padding(table, (0, 0, 0, 2))
        console.print(padding)
        console.print(f"Repository URL: {self._get_repo(poetry)}", end="\n\n")
        console.print(f"Mira https://baloto.com para mas informacion.", new_line_start=True)
        console.line()

        return 0

    @staticmethod
    def _get_what_is_miloto(poetry: Poetry) -> str:
        tool = poetry.get_tool()
        return tool.get("miloto", {}).get("description", "[warning]no esta definido[/]")

    @staticmethod
    def _get_what_is_baloto(poetry: Poetry) -> str:
        tool = poetry.get_tool()
        return tool.get("baloto", {}).get("description", "[warning]no esta definido[/]")

    @staticmethod
    def _get_repo(poetry: Poetry) -> str:
        project = poetry.get_project()
        return project.get("urls", {}).get("Repository", "[warning]no esta definido[/]")