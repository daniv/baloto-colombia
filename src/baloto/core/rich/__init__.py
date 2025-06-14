# Project : baloto-colombia
# File Name : __init__.py
# Dir Path : src/baloto/core/rich
# Created on: 2025–06–10 at 22:47:13.

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

__all__ = ("create_link_markup",)


def create_link_markup(filepath: str, lineno: int) -> str:
    path = Path(filepath)
    filename = path.name
    linkname = f"{filename}_{lineno}"
    return f"[bright_blue][link={path.as_posix()}:{lineno}][bright_blue u]{linkname}[/link][/] <-click[/]"
