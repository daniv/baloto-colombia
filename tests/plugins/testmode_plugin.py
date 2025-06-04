# - Project   : baloto-colombia
# - User Naem : solma
# - File Name : debug_mode_plugin.py
# - Dir Path  : tests/plugins
# - Created on: 2025-06-03 at 18:45:12

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    pass

@pytest.hookimpl(tryfirst=True)
def pytest_cmdline_main(config: pytest.Config) -> pytest.ExitCode | int | None:
    # from itertools import product
    # combinations8 = list(product(range(2), repeat=8))
    # combinations8 = list(filter(lambda x: sum(x) == 5, combinations8))
    # combinations10 = list(product(range(2), repeat=10))
    # combinations10 = list(filter(lambda x: sum(x) == 5, combinations10))

    if not "--strict-markers" in config.invocation_params.args:
        config.option.strict_markers = True
    if not "--strict-config" in config.invocation_params.args:
        config.option.strict_config = True

    if bool(os.getenv("TESTMODE", False)):
        from baloto.miloto.config.poetry.poetry import Poetry
        from baloto.utils import is_pydevd_mode
        from glom import glom

        poetry = Poetry.create_poetry(config.rootpath)
        data = poetry.pyproject.data
        testmode = glom(data, "tool.miloto.testmode")
        for k, v in testmode.items():
            code = f"config.option.{k} = {v}"
            compiled_code = compile(code, '<string>', 'exec')
            exec(compiled_code)

        if is_pydevd_mode():
            if not config.option.shwofixtures:
                config.option.shwofixtures = True
            if config.option.maxfail == 1:
                config.option.maxfail = 1
            if not config.option.runxfail:
                config.option.runxfail = True
            config.option.verbose = 1
            config.option.reportchars = "fExXs"

    return None

