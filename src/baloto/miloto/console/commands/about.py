from __future__ import annotations

from typing import TYPE_CHECKING

from glom import glom

from baloto.miloto.console.commands.command import Command as BalotoCommand
from baloto.miloto.exceptions.errors import BalotoRuntimeError

if TYPE_CHECKING:
    from rich.console import Console


class AboutCommand(BalotoCommand):
    name = "about"

    description = "Shows information about [prog]Miloto[/] application."

    def __init__(self):
        super().__init__()

        self.console: Console | None = None

    def setup(self) -> int:
        self.console = self.io.output.console
        return 0

    def handle(self) -> int:
        from rich.padding import Padding
        import platform

        app = self.get_application()
        py_version = platform.python_version()

        try:
            top_levels = self.miloto.poetry.get_top_levels()
        except BalotoRuntimeError as e:
            self.io.error_output.line()
            e.write(self.io)
            self.io.error_output.line()
            return e.exit_code

        app_name = self.get_application().name
        self.console.line()
        self.console.print(f"¿QUE ES {app_name.upper()}?", style="bold")
        padding = Padding(self._get_what_is_miloto(), (0, 0, 0, 2))

        self.console.print(padding, new_line_start=True)
        self.console.print(f"Version de [prog]Baloto Project[/]: [repr.number]{app.version}[/]")
        self.console.print(f"Version de [prog]Python[/]        : [repr.number]{py_version}[/]")
        self.console.line()
        self.console.print("PAQUETES INSTALADOS:", style="bold", new_line_start=True)
        from rich.table import Table

        from rich import box

        table = Table(box=box.SIMPLE_HEAD, show_header=True, show_edge=False, show_lines=False)
        table.add_column("Package", style="prog", width=20)
        table.add_column("Version", style="repr.number", width=10)
        table.add_column("Última version", width=10)
        table.add_column("Grupos", style="bold", width=10)
        table.add_column("Descripción", width=90, overflow="fold")

        for tl in top_levels:
            lt = f"[{{tag}}]{tl.get("latest")}[/]"
            latest = (
                lt.format(tag="green")
                if tl.get("version") == tl.get("latest")
                else lt.format(tag="yellow")
            )
            table.add_row(
                tl.get("name"),
                tl.get("version"),
                latest,
                ", ".join(tl.get("groups")),
                tl.get("description"),
            )
        padding = Padding(table, (0, 0, 0, 2))
        self.console.print(padding)
        self.console.print(f"Repository URL: {self._get_repo()}", end="\n\n")
        self.console.print(f"Mira https://baloto.com para mas informacion.", new_line_start=True)
        self.console.line()

        return 0

    def _get_what_is_miloto(self) -> str:
        data = self.miloto.poetry.pyproject.data
        return glom(data, "tool.miloto.description", default="[warning]no esta definido[/]")

    def _get_repo(self) -> str:
        data = self.miloto.poetry.pyproject.data
        return glom(data, "project.urls.Repository", default="[warning]no esta definido[/]")
