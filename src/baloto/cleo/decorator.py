# - Project   : baloto-colombia
# - User Naem : solma
# - File Name : decorator.py
# - Dir Path  : src/baloto/utils
# - Created on: 2025-05-31 at 03:07:14

from __future__ import annotations

import functools
import sys
from typing import Any
from typing import Callable, TYPE_CHECKING

from baloto.cleo.io.outputs.output import VVV
from baloto.cleo.io.outputs.output import Verbosity
from baloto.cleo.rich.factory.console_factory import ConsoleFactory

if TYPE_CHECKING:
    from rich.console import Console

__all__ = ("set_rich_console", "get_rich_console", "log", "set_verbositye")

WINDOWS = sys.platform == "win32"
DecoratorInfo = Callable[[Any, tuple[Any, ...], dict[str, Any]], None]
Decorater = Callable[[Any], Callable[[Any, tuple[Any, ...], dict[str, Any]], None]] | Callable[
    [Any, tuple[Any, ...], dict[str, Any]], None]


# Global console used by alternative print
_console: Console | None = None
_verbosity: Verbosity = Verbosity.QUIET



# def set_verbositye(level: Verbosity) -> None:
#     global _verbosity
#
#     _verbosity = level
#
# def set_rich_console(console: Console) -> None:
#     global _console
#
#     _console = console
#
# def get_rich_console() -> Console:
#     global _console
#     if _console is None:
#         from rich.console import Console
#
#         _console = ConsoleFactory.console_output()
#
#     return _console
#
# def log(_func: Callable[...] = None, *, call: bool = True, retval: bool = False, exc: bool = True, verbosity: Verbosity = VVV) -> Decorater:
#     global _verbosity
#     global _console
#
#     # if _verbosity == Verbosity.QUIET:
#     #     return None
#
#     def log_decorator_info(func) -> DecoratorInfo:
#
#         @functools.wraps(func)
#         def log_decorator_wrapper(self, *args, **kwargs) -> None:
#             """Build logger object"""
#             logger = _console
#             if not _console:
#                 logger = get_rich_console()
#
#             """log function begining"""
#             func_path = f"{self.__class__.__module__}.{self.__class__.__qualname__}.{func.__name__}"
#             if call and self:
#                 logger.log(f" [bright_yellow]-->[/] {func_path}()", style="italic")
#             try:
#                 """ log return value from the function """
#                 value = func(self, *args, **kwargs)
#                 if retval and self:
#                     logger.log(f" [bright_yellow]<--[/] {func_path}: {value!r}", style="italic")
#                 elif self:
#                     logger.log(f" [bright_yellow]<--[/] {func_path}", style="italic")
#             except:
#                 """log exception if occurs in function"""
#                 if exc and self:
#                     logger.log(f" [bright_red]<->[/]{func_path}: {str(sys.exc_info()[1])}", style="italic red")
#                 raise
#             return value
#         return log_decorator_wrapper
#     if _func is None:
#         return log_decorator_info
#     else:
#         return log_decorator_info(_func)
