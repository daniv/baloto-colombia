"""
https://github.com/TvoroG/pytest-lazy-fixture

"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pytest
from rich.console import Console

from baloto.cleo.rich.factory.console_factory import ConsoleFactory

# from tests import AllureStepLogger

if TYPE_CHECKING:
    from rich.console import Console


def pytest_configure(config: pytest.Config) -> None:
    from baloto.cleo.rich.logging.console_handler import ConsoleHandler
    from baloto.cleo.rich.factory.console_factory import ConsoleFactory

    from _pytest.logging import get_log_level_for_setting

    log_cli_level = get_log_level_for_setting(config, "log_cli_level", "log_level")
    enabled = config.getoption("--log-cli-level") is not None or config.getini("log_cli")
    console = ConsoleFactory.console_output()
    console.print("C:/Users/solma/PycharmProjects/baloto-colombia/tests/conftest.py:95")
    rich_tracebacks = tracebacks_show_locals = True
    if enabled:
        console = ConsoleFactory.console_output()
        handler = ConsoleHandler(
            level=log_cli_level,
            console=console,
            rich_tracebacks=rich_tracebacks,
            tracebacks_show_locals=tracebacks_show_locals,
        )
        # from rich.logging import RichHandler
        # handler = RichHandler(
        #     console=console, level=log_cli_level,
        #     show_time=False,
        #     rich_tracebacks=rich_tracebacks,
        #     tracebacks_show_locals=tracebacks_show_locals
        # )
        # formatter = ConsoleFormatter(
        #     rich_tracebacks=rich_tracebacks
        # )
        # handler.setFormatter(formatter)
        # if not io.is_very_verbose():
        #     handler.addFilter(POETRY_FILTER)

        # FORMAT = "%(asctime)-15s - %(levelname)s - %(message)s"
        logging.basicConfig(
            level="NOTSET",
            format="%(message)s",
            datefmt="[%X]",
            handlers=[handler],
        )

        from time import sleep

        log = logging.getLogger("conftest")
        log.info("Server starting...")

        log.info("Listening on http://127.0.0.1:8080")
        # sleep(1)

        log.info("GET /index.html 200 1298")
        log.info("GET /imgs/backgrounds/back1.jpg 200 54386")
        log.info("GET /css/styles.css 200 54386")
        log.warning("GET /favicon.ico 404 242")
        # sleep(1)

        log.debug(
            "JSONRPC request\n--> %r\n<-- %r",
            {
                "version": "1.1",
                "method": "confirmFruitPurchase",
                "params": [["apple", "orange", "mangoes", "pomelo"], 1.123],
                "id": "194521489",
            },
            {"version": "1.1", "result": True, "error": None, "id": "194521489"},
        )
        log.debug(
            "Loading configuration file /adasd/asdasd/qeqwe/qwrqwrqwr/sdgsdgsdg/werwerwer/dfgerert/ertertert/ertetert/werwerwer"
        )
        log.error("Unable to find 'pomelo' in database!")
        log.info("POST /jsonrpc/ 200 65532")
        log.info("POST /admin/ 401 42234")
        log.warning("password was rejected for admin site.")

        def divide() -> None:
            number = 1
            divisor = 0
            foos = ["foo"] * 100
            log.debug("in divide")
            try:
                number / divisor
            except:
                log.exception("An error of some kind occurred!")

        divide()
        sleep(1)
        log.critical("Out of memory!")
        log.info("Server exited with code=-1")
        log.info("[bold]EXITING...[/bold]", extra=dict(markup=True))
        i = 0


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

    config.option.ignore_glob = ["*__init*", "*.log"]
    return None


@pytest.fixture(scope="session")
def console_output() -> Console:
    return ConsoleFactory.console_output()
