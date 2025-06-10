# Project : baloto-colombia
# File Name : traceback.py
# Dir Path : tests/plugins
# Created on: 2025–06–05 at 22:42:10.

from __future__ import annotations

from enum import StrEnum
from typing import Any
from typing import Sequence
from typing import TYPE_CHECKING
from typing import Type

import pytest
from rich.traceback import Traceback

from baloto.cleo.io.outputs.output import Verbosity
from helpers import add_option_ini

if TYPE_CHECKING:
    from rich.traceback import Trace, TracebackType

__all__ = ("PLUGIN_NAME", "TracebackOptions", "traceback", "from_exception", "extract")

PLUGIN_NAME = "miloto-traceback"


class TracebackOptions(StrEnum):
    EXTRA_LINES = "tracebacks_extra_lines"
    THEME = "tracebacks_theme"
    SHOW_LOCALS = "tracebacks_show_locals"


@pytest.hookimpl
def pytest_addoption(parser: pytest.Parser, pluginmanager: pytest.PytestPluginManager) -> None:
    group = parser.getgroup(
        "tracebacks", "Configuration for displaying rich-tracebacks", after="miloto"
    )

    # noinspection PyTypeChecker
    parser.addini(
        TracebackOptions.EXTRA_LINES,
        type="int",
        default=3,
        help="Additional lines of code to render tracebacks. Defaults is %(default)s.",
    )
    add_option_ini(
        parser,
        group,
        opts=["--tracebacks-theme", "--theme"],
        dest=TracebackOptions.THEME,
        default="miloto_dark",
        ini_type="string",
        opt_type=str,
        help="Override pygments theme used in traceback. Defaults to '%(default)s'",
    )
    group.addoption(
        "--tracebacks-show-locals",
        action="store_true",
        dest=TracebackOptions.SHOW_LOCALS,
        help="Enable display of locals in tracebacks. Defaults to %(default)s.",
    )


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config: pytest.Config) -> None:
    from _pytest.logging import get_option_ini

    theme = get_option_ini(config, TracebackOptions.THEME)
    if theme == "miloto_dark":
        from baloto.cleo.rich.theme import MilotoSyntaxTheme

        config.option.tracebacks_theme = MilotoSyntaxTheme()

    # from tests import get_console_key, create_console_key
    # console_key = get_console_key()
    # console = config.stash.get(console_key, None)
    # if console is None:
    #     console = create_console_key(config)
    import sys

    verbose = config.option.verbose
    show_locals = config.getoption(TracebackOptions.SHOW_LOCALS)
    if not show_locals:
        if verbose > Verbosity.NORMAL:
            config.option.tracebacks_show_locals = True

    if verbose == Verbosity.NORMAL:
        config.option.tracebacks_max_frames = 5
    elif verbose == Verbosity.VERBOSE:
        config.option.tracebacks_max_frames = 10


def from_exception(
    config: pytest.Config,
    exc_type: Type[BaseException],
    exc_value: BaseException,
    tb: TracebackType | None,
    **kwargs: Sequence[str, Any],
) -> Traceback:
    """Create a traceback from exception info

    :param config: The pytest Config instance
    :param exc_type: Exception type.
    :param exc_value: Exception value.
    :param tb: Python Traceback object.
    :param kwargs: Additional argument
    :return: a Renderable Traceback instance.
    """
    rich_traceback = extract(config, exc_type, exc_value, tb, **kwargs)
    return traceback(config, rich_traceback, **kwargs)


def traceback(config: pytest.Config, trace: Trace | None, **kwargs: object) -> Traceback:
    """Produce A Console renderable that renders a traceback.

    :param config: The pytest Config instance
    :param trace: A `Trace` object produced from `extract` see :class:`~rich.tracebacks.Trace <rich.Trace>`
    :param kwargs: additional keyword arguments see :class:`~rich.tracebacks.Traceback <rich.Traceback>`
    :return: a ConsoleRenderable instanse of Traceback type
    """
    from _pytest.logging import get_option_ini

    if not TracebackOptions.EXTRA_LINES in kwargs:
        kwargs["extra_lines"] = config.getini(TracebackOptions.EXTRA_LINES)

    if not TracebackOptions.THEME in kwargs:
        kwargs["theme"] = get_option_ini(config, TracebackOptions.THEME)

    if not TracebackOptions.SHOW_LOCALS in kwargs:
        kwargs["show_locals"] = get_option_ini(config, TracebackOptions.SHOW_LOCALS)

    if trace:
        kwargs.pop("show_locals", None)
        kwargs.pop("locals_max_length", None)
        kwargs.pop("locals_max_string", None)
        kwargs.pop("locals_hide_dunder", None)
        kwargs.pop("locals_hide_sunder", None)

    return Traceback(trace, **kwargs)


def extract(
    config: pytest.Config,
    exc_type: Type[BaseException],
    exc_value: BaseException,
    tb: TracebackType | None,
    **kwargs: object,
) -> Trace:
    """Extract traceback information.

    :param config: The pytest Config instance
    :param exc_type: Exception type.
    :param exc_value: Exception value.
    :param tb: Python Traceback object.
    :param kwargs: Additional keyword arguments. see :meth:`rich.tracebacks.Traceback.extract <rich.tracebacks.Traceback.extract>`
    :return: a Trace object
    """
    getoption = config.getoption

    if not "show_locals" in kwargs:
        kwargs["show_locals"] = getoption(TracebackOptions.SHOW_LOCALS)

    return Traceback.extract(exc_type, exc_value, tb, **kwargs)
