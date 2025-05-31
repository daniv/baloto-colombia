from __future__ import annotations


class TOMLKitError(Exception):
    pass


class PoetryError(Exception):
    pass


class TOMLError(TOMLKitError, PoetryError):
    pass
