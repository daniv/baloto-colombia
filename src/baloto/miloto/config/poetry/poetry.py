from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any
from typing import TYPE_CHECKING

from baloto.cleo.io.null_io import NullIO
from baloto.miloto.config.poetry.toml import PyProjectTOML
from baloto.miloto.exceptions.errors import BalotoRuntimeError

if TYPE_CHECKING:
    from baloto.cleo.io.io import IO
    from baloto.miloto.config.poetry.locker import Locker
    from baloto.miloto.config.poetry.file import TOMLFile


class BasePoetry:
    def __init__(self, file: Path, pyproject_type: type[PyProjectTOML] = PyProjectTOML) -> None:
        self._pyproject = pyproject_type(file)
        self.version: str | None = None
        self.name: str | None = None

    @classmethod
    def create_poetry(cls, cwd: Path | None = None) -> BasePoetry:
        from baloto.miloto.config.poetry.toml import PyProjectTOML

        poetry_file = cls.locate(cwd)
        pyproject = PyProjectTOML(path=poetry_file)
        project = pyproject.data.get("project", {})
        name = project.get("name")
        assert isinstance(name, str)
        version = project.get("version", "0")
        assert isinstance(version, str)

        poetry = BasePoetry(poetry_file)
        poetry.version = version
        poetry.name = name
        return poetry

    @property
    def pyproject(self) -> PyProjectTOML:
        return self._pyproject

    @property
    def pyproject_path(self) -> Path:
        return self._pyproject.path

    @classmethod
    def locate(cls, cwd: Path | None = None) -> Path:
        cwd = Path(cwd or Path.cwd())
        candidates = [cwd]
        candidates.extend(cwd.parents)

        for path in candidates:
            poetry_file = path / "pyproject.toml"

            if poetry_file.exists():
                return poetry_file

        else:
            raise BalotoRuntimeError(
                    f"Poetry could not find a 'pyproject.toml' file in {cwd} or its parents"
            )


class Poetry(BasePoetry):
    def __init__(self, file: Path, locker: Locker, io: IO | None = None) -> None:
        super().__init__(file, pyproject_type=PyProjectTOML)
        self._locker = locker
        self._io = io

    @property
    def file(self) -> TOMLFile:
        return self.pyproject.file

    @property
    def locker(self) -> Locker:
        return self._locker

    @classmethod
    def create_poetry(cls, cwd: Path | None = None, io: IO | None = None) -> Poetry:
        if io is None:
            io = NullIO()

        base_poetry = super().create_poetry(cwd=cwd)
        poetry_file = base_poetry.pyproject_path
        from baloto.miloto.config.poetry.locker import Locker

        locker = Locker(poetry_file.parent / "poetry.lock", base_poetry.pyproject.data)

        poetry = Poetry(poetry_file, locker, io)
        return poetry

    # def get_project(self) -> Mapping[str, Any]:
    #     return self.pyproject.data.get("project", {})
    #
    # def get_tool(self) -> dict[str, Any]:
    #     return self.pyproject.data.get("tool", {})

    def get_top_levels(self) -> list[dict[str, Any]]:

        show_top_level_data = []

        if not self.locker.is_locked():
            from baloto.miloto.console.console_message import ConsoleMessage

            message = ConsoleMessage(
                message="Error: [c1]poetry.lock[/] file not found. Run [command]poetry lock[/] to create it."
            )
            raise BalotoRuntimeError(
                reason=f"not self.locker.is_locked() return False", messages=[message], exit_code=1
            )

        import shlex

        command_line = "poetry show --top-level --latest --no-ansi"
        args = shlex.split(command_line)
        try:
            result = subprocess.run(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                shell=True,
                check=True,
            )
            out_list = list(filter(lambda x: x != "", result.stdout.split("\n")))

            def name_latest(x) -> tuple[str, str]:
                filtered = list(filter(lambda da: da != "", x.split(" ")))
                return filtered[0], filtered[2]

            names_and_latest = list(map(lambda x: name_latest(x), out_list))
            names = list(map(lambda x: x[0], names_and_latest))

            packages = list(
                filter(lambda x: x.get("name") in names, self.locker.lock_data.get("package"))
            )
            for name, latest in names_and_latest:
                pack = next(filter(lambda x: x.get("name") == name, packages), {})
                if pack:
                    pack["latest"] = latest
                    show_top_level_data.append(pack)

            return show_top_level_data

        except subprocess.CalledProcessError as e:
            raise BalotoRuntimeError.create(
                reason=f"Failed to execute subprocess: [command]{command_line}[/]",
                exception=e,
                info=[str(e), e.stderr],
            )
