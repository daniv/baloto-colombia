# - Project   : baloto-colombia
# - User Naem : solma
# - File Name : miloto.py
# - Dir Path  : src/baloto/miloto
# - Created on: 2025-05-31 at 05:01:52

from __future__ import annotations

from typing import Any
from typing import IO
from typing import Mapping
from typing import TYPE_CHECKING

from baloto.miloto.config.poetry.poetry import Poetry

if TYPE_CHECKING:
    from pathlib import Path

__all__ = ("Miloto", )

class Miloto:
    def __init__(self, cwd: Path, io: IO):
        self._poetry: Poetry | None = None
        self.project_directory = cwd
        self.io = io

    @property
    def poetry(self, project_directory: Path | None = None) -> Poetry:
        from baloto.miloto.config.poetry.poetry import Poetry

        if self._poetry is not None:
            return self._poetry

        self._poetry = Poetry.create_poetry(cwd=project_directory, io=self.io)

        return self._poetry

    def get_poetry_data(self) -> Mapping[str, Any]:
        return self.poetry.pyproject.data