# - Project   : baloto-colombia
# - User Naem : solma
# - File Name : difflib_diff.py
# - Dir Path  : tests
# - Created on: 2025-06-01 at 14:07:04
# - See       : https://github.com/ni/py_better_diff/blob/main/better_diff/unified_plus.py

from __future__ import annotations

import collections
import difflib
from typing import TYPE_CHECKING, Deque

if TYPE_CHECKING:
    pass

__all__ = ()


def format_diff(a: str, b: str, fromfile: str = "a", tofile: str = "b") -> str:
    """Return a unified+ diff between two strings.

    Args:
        a: The first string to compare.
        b: The second string to compare.
        fromfile: The name of the first file.
        tofile: The name of the second file.
    """
    result: list[str] = []
    last_line: str | None = None

    normalized_endings_a, normalized_endings_b = (a.rstrip("\r\n"), b.rstrip("\r\n"))
    newline_difference_message = "\n\\ Newline at end of file"

    len_a_difference = len(a) - len(normalized_endings_a)
    len_b_difference = len(b) - len(normalized_endings_b)
    if len_a_difference != len_b_difference:
        normalized_endings_a += newline_difference_message * (len(a) - len(normalized_endings_a))
        normalized_endings_b += newline_difference_message * (len(b) - len(normalized_endings_b))

    dangling_whitespace_run: Deque[str] = collections.deque()

    for line in difflib.unified_diff(
        a=normalized_endings_a.splitlines(),
        b=normalized_endings_b.splitlines(),
        fromfile=fromfile,
        tofile=tofile,
    ):
        if last_line and line:
            doing_a_substitution = last_line.startswith("-") and line.startswith("+")
            last_line_had_dangling_whitespace = last_line != last_line.rstrip()
            new_line_is_last_line_without_whitespace = last_line[1:].rstrip() == line[1:]
            if all(
                [
                    doing_a_substitution,
                    last_line_had_dangling_whitespace,
                    new_line_is_last_line_without_whitespace,
                ]
            ):
                _highlight_dangling_whitespace(result, last_line, line)

            elif dangling_whitespace_run and line.startswith("+"):
                if line[1:].rstrip() == dangling_whitespace_run[0][1:].rstrip():
                    old_line = dangling_whitespace_run.popleft()
                    result.append(old_line)
                    _highlight_dangling_whitespace(result, old_line, line)
                    result.append(line)

                    continue
                else:
                    _dump_dangling_whitespace_run(result, dangling_whitespace_run)

            elif last_line_had_dangling_whitespace:
                we_may_be_continuing = line.startswith("-")
                if we_may_be_continuing:
                    dangling_whitespace_run.append(line)
                    continue  # don't print this one yet
                else:
                    _dump_dangling_whitespace_run(result, dangling_whitespace_run)

        result.append(line.rstrip())
        last_line = line

    _dump_dangling_whitespace_run(result, dangling_whitespace_run)

    if not result:
        return ""
    return "\n".join(result) + "\n"


def _highlight_dangling_whitespace(result, last_line, line):
    """Insert a highlight line for dangling whitespace."""
    highlight = "^" * (len(last_line) - len(last_line.rstrip()))
    result.append("?" + " " * (len(line) - 1) + highlight)


def _dump_dangling_whitespace_run(result: list, dangling_whitespace_run: collections.deque) -> None:
    """Dump the dangling whitespace run to the result."""
    while dangling_whitespace_run:
        old_line = dangling_whitespace_run.popleft()
        result.append(old_line)