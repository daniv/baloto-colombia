from __future__ import annotations

from pathlib import Path
from typing import Any


from baloto.core.poetry.exceptions import PoetryError
from baloto.core.poetry.file import TOMLFile


class PyProjectTOML:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._toml_file = TOMLFile(path=path)
        self._data: dict[str, Any] | None = None

    @property
    def path(self) -> Path:
        return self._path

    @property
    def file(self) -> TOMLFile:
        return self._toml_file

    @property
    def data(self) -> dict[str, Any]:
        import tomllib

        if self._data is None:
            if not self.path.exists():
                self._data = {}
            else:
                try:
                    with self.path.open("rb") as f:
                        self._data = tomllib.load(f)
                except tomllib.TOMLDecodeError as e:
                    msg = (
                        f"{self._path.as_posix()} is not a valid TOML file.\n"
                        f"{e.__class__.__name__}: {e}"
                    )

                    if str(e).startswith("Cannot overwrite a value"):
                        msg += "\nThis is often caused by a duplicate entry."

                    raise PoetryError(msg) from e

        return self._data