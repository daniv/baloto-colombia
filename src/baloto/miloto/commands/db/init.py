from __future__ import annotations

import sqlite3
from typing import ClassVar
from typing import TYPE_CHECKING

from baloto.core.commands.database_command import DatabaseCommand

if TYPE_CHECKING:
    from rich.console import Console


class DbInitCommand(DatabaseCommand):
    name = "db init"

    description = "Initializes the databasa by adding tables to sqlite3."
    aliases: ClassVar[list[str]] = ["ini"]

    def __init__(self) -> None:
        super().__init__()

        self.console: Console | None = None

    def setup(self) -> int:
        return super().setup()

    def handle(self) -> int:
        try:
            with sqlite3.connect(self.database_file) as conn:
                cursor = conn.cursor()
                for statement in sql_statements:
                    cursor.execute(statement)
                conn.commit()

        except sqlite3.OperationalError as e:
            print("Failed to create tables:", e)

        return 0


sql_statements = [
    """CREATE TABLE IF NOT EXISTS sessions (
            lottery_id INTEGER PRIMARY KEY, 
            lottery_date DATE NOT NULL UNIQUE,
            accumulated INT NOT NULL
        );""",
    """CREATE UNIQUE INDEX IF NOT EXISTS l_id ON sessions(lottery_id);""",
    """CREATE UNIQUE INDEX IF NOT EXISTS l_id_date ON sessions(lottery_id, lottery_date);""",
]


# this.cur.execute("""
#     INSERT OR IGNORE INTO sessions (lottery_id, lottery_date, accumulated)
#     VALUES (1, '2025-10-01', 120);
#     """);
