from __future__ import annotations

import hashlib
import io
import logging
import os
import shutil
import stat
import sys
import tarfile
import tempfile
import zipfile

from collections.abc import Mapping
from contextlib import contextmanager
from contextlib import suppress
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any
from typing import overload

# from requests.exceptions import ChunkedEncodingError
# from requests.exceptions import ConnectionError
# from requests.utils import atomic_open

if TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Collection
    from collections.abc import Iterator
    from types import TracebackType

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


def ensure_path(path: str | Path, is_directory: bool = False) -> Path:
    if isinstance(path, str):
        path = Path(path)

    if path.exists() and path.is_dir() == is_directory:
        return path

    raise ValueError(
        f"Specified path '{path}' is not a valid {'directory' if is_directory else 'file'}."
    )
