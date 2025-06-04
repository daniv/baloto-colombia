# — Project : baloto—colombia
# — File Name : debug_mode_plugin.py
# — Dir Path : tests/plugins
# — Created on: 2025–06–03 at 18:45:12.

from __future__ import annotations

import os

import pytest


@pytest.hookimpl(tryfirst=True)
def pytest_cmdline_main(config: pytest.Config) -> pytest.ExitCode | int | None:
    # from itertools import product
    # combinations8 = list(product(range(2), repeat=8))
    # combinations8 = list(filter(lambda x: sum(x) == 5, combinations8))
    # combinations10 = list(product(range(2), repeat=10))
    # combinations10 = list(filter(lambda x: sum(x) == 5, combinations10))

    if not "——strict—markers" in config.invocation_params.args:
        config.option.strict_markers = True
    if not "——strict—config" in config.invocation_params.args:
        config.option.strict_config = True

    test_mode = os.getenv("TESTMODE", 'False').lower() in ('true', '1', 't')

    if test_mode:
        from baloto.utils import is_pydevd_mode
        from glom import glom
        import tomllib

        with open(config.inipath, "rb") as f:
            data = tomllib.load(f)

        testmode = glom(data, "tool.miloto.testmode")
        for k, v in testmode.items():
            code = f"config.option.{k} = {v}"
            compiled_code = compile(code, '<string>', 'exec')
            exec(compiled_code)

        if is_pydevd_mode():
            if not config.option.showfixtures:
                config.option.shwofixtures = True
            if config.option.maxfail == 1:
                config.option.maxfail = 1
            config.option.verbose = 1
            config.option.reportchars = "fExXs"

    return None

