from __future__ import annotations

from abc import ABC
import sqlite3
from typing import TYPE_CHECKING

from baloto.core.commands.command import Command as BalotoCommand


if TYPE_CHECKING:

    from baloto.core.cleo.io.inputs.option import Option
    from baloto.core.cleo.io.inputs.argument import Argument
    from pathlib import Path
    from rich.console import Console
    from baloto.core.poetry.poetry import Poetry


class DatabaseCommand(BalotoCommand, ABC):
    def __init__(self):
        super().__init__()

        self.console: Console | None = None
        self.error_console: Console | None = None
        self.database_file: Path | None = None
        self.db_file_name = "db.sqlite3"

    def setup(self) -> int:
        self.console = self.io.console
        self.error_console = self.io.error_console
        self.database_file = self.poetry.pyproject_path.parent / self.db_file_name
        connection: sqlite3.Connection | None = None

        if self.database_file.exists():
            if self.io.is_verbose():
                posix = self.database_file.as_posix()
                self.console.print(f"The database file {posix} already exists")
            return 0

        try:
            connection = sqlite3.connect(self.database_file)
            if self.io.is_verbose():
                self.console.print(
                    f"  [info]-[/] Connection test; database {self.database_file} connected."
                )
        except sqlite3.Error as error:
            self.error_console.print("[error]Failed to connect with sqlite3 database[/]", error)
            return 1
        finally:
            if connection:
                connection.close()
                if self.io.is_verbose():
                    self.console.print("  [info]-[/] The sqlite connection was closed")

        return 0
