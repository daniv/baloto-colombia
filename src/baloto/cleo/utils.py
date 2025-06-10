# - Project   : baloto-colombia
# - User Naem : solma
# - File Name : utils.py
# - Dir Path  : src/baloto/cleo
# - Created on: 2025-05-30 at 21:45:50

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from rich.console import WINDOWS

if TYPE_CHECKING:
    from pathlib import Path
    from baloto.utils.types import PathStr


__all__ = ("find_similar_names", "escape_trailing_backslash", "escape", "shell_quote", "safe_str", "markup_path", "markup_loation")


def find_similar_names(name: str, names: list[str]) -> list[str]:
    """
    Finds names matching to a given command name.
    """
    from difflib import SequenceMatcher
    threshold = 0.4
    distance_by_name = {}
    if " " in name:
        names = [name for name in names if " " in name]
    for actual_name in names:
        distance = SequenceMatcher(None, actual_name, name).ratio()

        is_similar = distance <= len(name) / 3
        substring_index = actual_name.find(name)
        is_substring = substring_index != -1

        if is_similar or is_substring:
            distance_by_name[actual_name] = (
                distance,
                substring_index if is_substring else float("inf"),
            )

    # Only keep results with a distance below the threshold
    distance_by_name = {key: value for key, value in distance_by_name.items() if value[0] > threshold}
    # Display results with shortest distance first
    return sorted(distance_by_name, key=lambda key: distance_by_name[key])


def shell_quote(token: str) -> str:
    import shlex
    import subprocess
    if WINDOWS:
        return subprocess.list2cmdline([token])

    return shlex.quote(token)


def escape(text: str) -> str:
    """
    Escapes "<" special char in given text.
    """
    text = re.sub(r"([^\\]?)<", "\\1\\<", text)

    return escape_trailing_backslash(text)


def escape_trailing_backslash(text: str) -> str:
    """
    Escapes trailing "\\" in given text.
    """
    if text.endswith("\\"):
        length = len(text)
        text = text.rstrip("\\").replace("\0", "").ljust(length, "\0")

    return text

def safe_str(_object: Any) -> str:
    """Don't allow exceptions from __str__ to propagate."""
    try:
        return str(_object)
    except Exception:
        return "<exception str() failed>"

def markup_loation(filename: PathStr, lineno: int, *, relative_to: PathStr = None) -> str:
    markup = markup_path(filename, relative_to=relative_to)
    return f"{markup}:{lineno}"
