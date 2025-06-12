# - Project   : baloto-colombia
# - File Name : helpers.py
# - Dir Path  : tests
# - Created on: 2025-05-29 at 19:57:54

from __future__ import annotations

from typing import Any
from collections.abc import Callable
from typing import Literal
from collections.abc import Sequence
from typing import Type
from typing import TypeVar

import pytest
from typing_extensions import TYPE_CHECKING

if TYPE_CHECKING:
    from _pytest.config.argparsing import OptionGroup
    _PluggyPlugin = object


def cleanup_factory(config: pytest.Config, plugin: _PluggyPlugin) -> Callable[[], Any]:
    """Unregisters a plugin as a callback for
    see :meth:`~pytest.Config.add_cleanup`

    :param config: The pytest Config instance
    :param plugin: The pytest plugin instance to unregister
    :return: None
    """
    def clean_up() -> None:
        pluginmanager = config.pluginmanager
        name = pluginmanager.get_name(plugin)
        if name:
            pluginmanager.unregister(name=name)
    return clean_up


def add_option_ini(
        parser: pytest.Parser,
        group: OptionGroup,
        *,
        opts: Sequence[str],
        dest: str,
        default: Any = None,
        ini_type: str| None = None,
        opt_type: Type[str | int | None] = None,
        **kwargs: Sequence[str]
) -> None:
    """ Adds an ini option to pytest.Parser.
    uses both methods :py:func:`config.getoption(name) <pytest.Config.getini>` and :py:func:`config.getini(name) <pytest.Config.getini>`

    see
        - :class:`_pytest.config.argparsing.OptionGroup` for how to use.
        - :class:`_pytest.config.argparsing.Parser` for how to use.

    :param parser: The pytest Parser instance
    :param group: The group to add the option to; see :meth:`~_pytest.config.argparsing.Parser.getgroup`
    :param opts: names, can be short or long options.
    :param dest: Name of the ini-variable.
    :param default: Default value if no ini-file option exists but is queried.
    :param ini_type: The type of the ini variable from literalL["string", "paths", "pathlist", "args", "linelist", "bool", "int", "float"]
    :param opt_type: The type of the opt variable
    :param kwargs: additional arguments for the option see :py:func:`config.getini(name) <pytest.Config.getini>`.
    :return: None
    """
    parser.addini(
        dest, default=default, type=ini_type, help="Default value for " + opts[0]
    )
    if opt_type is None:
        group.addoption(*opts, dest=dest, **kwargs)
    else:
        group.addoption(*opts, type=opt_type, dest=dest, **kwargs)
