# Project : baloto-colombia
# File Name : bootstrap.py
# Dir Path : tests/plugins
# Created on: 2025–06–08 at 16:54:49.

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    pass

__all__ = ()


@pytest.hookimpl(tryfirst=True)
def pytest_cmdline_main(config: pytest.Config) -> pytest.ExitCode | int | None:
    if not "--strict—markers" in config.invocation_params.args:
        config.option.strict_markers = True
    if not "--strict—config" in config.invocation_params.args:
        config.option.strict_config = True

    return None


def pytest_cmdline_parse(
    pluginmanager: pytest.PytestPluginManager, args: list[str]
) -> pytest.Config | None:
    pass
