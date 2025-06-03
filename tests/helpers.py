# - Project   : baloto-colombia
# - File Name : helpers.py
# - Dir Path  : tests
# - Created on: 2025-05-29 at 19:57:54

from __future__ import annotations

import re
from typing import Pattern

"""
Determine if a string contains only whitespace characters or is empty.
"""
is_whitespace = lambda string: string.strip() == ""

"""
Determine if a string contains any of the given values. *matches* may be a
single string, or a list of strings.
"""
contains = lambda string, matches: any([m in string for m in ([matches] if isinstance(matches, str) else matches)])

"""
Determine if a string contains all of the given values.
"""
contains_all = lambda string, matches: all([m in string for m in matches])


def multi_replace(text: str, pairs: dict[str, str]) -> str:
    pairs = dict((re.escape(k), v) for k, v in pairs.items())
    pattern = re.compile("|".join(pairs.keys()))
    return pattern.sub(lambda m: pairs[re.escape(m.group(0))], text)

def sub_twice(regex: Pattern[str], replacement: str, original: str) -> str:
    """Replace `regex` with `replacement` twice on `original`.

    This is used by string normalization to perform replaces on
    overlapping matches.
    """
    return regex.sub(replacement, regex.sub(replacement, original))

class StopTest(BaseException):
    """Raised when a test should stop running and return control to
    the Hypothesis engine, which should then continue normally.
    """

    def __init__(self, testcounter: int) -> None:
        super().__init__(repr(testcounter))
        self.testcounter = testcounter