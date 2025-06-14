from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING

from typing_extensions import deprecated

# from requests.exceptions import ChunkedEncodingError
# from requests.exceptions import ConnectionError
# from requests.utils import atomic_open

if TYPE_CHECKING:
    from collections.abc import Iterator

    # from poetry.core.packages.package import Package
    # from requests import Response
    # from requests import Session


@contextmanager
def directory(path: Path) -> Iterator[Path]:
    cwd = Path.cwd()
    try:
        os.chdir(path)
        yield path
    finally:
        os.chdir(cwd)


@deprecated("Will move")
def ensure_path(path: str | Path, is_directory: bool = False) -> Path:
    if isinstance(path, str):
        path = Path(path)

    if path.exists() and path.is_dir() == is_directory:
        return path

    raise ValueError(
        f"Specified path '{path}' is not a valid {'directory' if is_directory else 'file'}."
    )
