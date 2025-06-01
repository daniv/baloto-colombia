# - Project   : baloto-colombia
# - File Name : helpers.py
# - Dir Path  : tests
# - Created on: 2025-05-29 at 19:57:54

from __future__ import annotations

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
