# Project : baloto-colombia
# File Name : hookspecs.py
# Dir Path : src/baloto/core/pytest_rich
# Created on: 2025–06–13 at 10:56:35.

from __future__ import annotations

from typing import TYPE_CHECKING

import pluggy

from baloto.core.config.config import RichConfig

if TYPE_CHECKING:
    from baloto.core.rich.tracebacks import SysExceptionInfo
    from rich.traceback import Traceback


__all__ = ("RichSpecs",)


hookspec = pluggy.HookspecMarker("rich")


class RichSpecs:
    @hookspec(historic=True)
    def rich_configure(self, config: RichConfig) -> None:
        pass

    def rich_unconfigure(self, config: RichConfig) -> None:
        pass

    def rich_internalerror(self, excinfo=SysExceptionInfo[BaseException]) -> Traceback | None:
        pass
