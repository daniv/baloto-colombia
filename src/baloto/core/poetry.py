from __future__ import annotations

from pathlib import Path
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from baloto.core.cleo.io.io import IO


class Poetry:
    def __init__(self, cwd: Path, io: IO):
        poetry_file = self._locate_pyproject(cwd)
        self._pyproject = self._read_toml_file(poetry_file)
        self._io = io

    @property
    def pyproject(self) -> dict[str, Any]:
        return self._pyproject

    @staticmethod
    def _locate_pyproject(cwd: Path | None = None) -> Path:

        cwd = Path(cwd or Path.cwd())
        candidates = [cwd]
        candidates.extend(cwd.parents)

        for path in candidates:
            poetry_file = path / "pyproject.toml"

            if poetry_file.exists():
                return poetry_file

        else:
            raise RuntimeError(
                f"Cleo could not find a pyproject.toml file in {cwd} or its parents"
            )

    @staticmethod
    def _read_toml_file(pyproject: Path) -> dict[str, Any]:
        import tomllib

        with open(pyproject, "rb") as poetry_file:
            toml_content = tomllib.load(poetry_file)
        return toml_content