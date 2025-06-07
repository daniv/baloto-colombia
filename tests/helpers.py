# - Project   : baloto-colombia
# - File Name : helpers.py
# - Dir Path  : tests
# - Created on: 2025-05-29 at 19:57:54

from __future__ import annotations

import re
from functools import lru_cache
from typing import Pattern, Any, Callable

import pytest

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

def cleanup_factory(config: pytest.Config, plugin: object) -> Callable[[], Any]:
    def clean_up() -> None:
        pluginmanager = config.pluginmanager
        name = pluginmanager.get_name(plugin)
        pluginmanager.unregister(name=name)
    return clean_up
