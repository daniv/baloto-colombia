# - Project   : baloto-colombia
# - User Naem : solma
# - File Name : alphabets.py
# - Dir Path  : tests
# - Created on: 2025-06-01 at 04:50:10

from __future__ import annotations

import itertools
import string
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


ALPHABET_ASCII_LOWER_UPPERS = list(itertools.chain(list(string.ascii_lowercase), list(string.ascii_uppercase)))