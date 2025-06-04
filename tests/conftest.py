"""
https://github.com/TvoroG/pytest-lazy-fixture

"""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, Any

import pytest
from rich.console import detect_legacy_windows

if TYPE_CHECKING:
    from rich.console import Console


DISABLE_PRINT = bool(int(os.getenv("DISABLE_PRINT", False)))
DISABLE_MSG = "run unit-test no requires printing env.DISABLE_PRINT was set to True"


# pytest.register_assert_rewrite("baloto.plugin.assertion_plugin.plugin")

def pytest_configure(config: pytest.Config) -> None:
    from baloto.cleo.rich.logging.console_handler import ConsoleHandler
    from baloto.cleo.rich.factory.console_factory import ConsoleFactory

    from _pytest.logging import get_log_level_for_setting

    log_cli_level = get_log_level_for_setting(config, "log_cli_level", "log_level")
    enabled = config.getoption("--log-cli-level") is not None or config.getini("log_cli")

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
def pytest_exception_interact(
    node: pytest.Item | pytest.Collector,
    call: pytest.CallInfo[Any],
    report: pytest.CollectReport | pytest.TestReport
) -> None:
    from tests.assert_report import AssertionErrorReport

    try:
        if call.excinfo.type is AssertionError:
            call.excinfo.value.add_note("The report was generated using pytest_exception_interact hook")
            print("")
            formatter = Formatter()
            from rich import box

            console = ConsoleFactory.console_output()
            formatter.set_text("jojowoorogoodfgo")
            c = formatter.render_rich_colors()
            console.print(c)

            aer = AssertionErrorReport(node, call, report)
            if aer.report_status:
                # console.print(aer)
                rend = aer.render(console)
                console.print(rend)
                # console.print(aer)
                console.rule("[bright_red]Stack Trace", characters="=", style="bright_red dim")
                # traceback = Traceback(show_locals=True, suppress=["pluggy"], theme="ansi_dark")
                # console.print(traceback)

    except* AssertionReportException as e:
        print(e)



@pytest.fixture(scope="session")
def console_output(record_testsuite_property) -> Console:
    from baloto.cleo.rich.factory.console_factory import ConsoleFactory
    return ConsoleFactory.console_output()


@pytest.fixture(scope="session", name="styled_console")
def create_styled_rich_console(record_testsuite_property) -> Console:
    from baloto.cleo.formatters.formatter import Formatter
    from rich.console import Console

    theme = Formatter().create_theme(None)
    console = Console(
            color_system="truecolor",
            force_terminal=True,
            theme=theme,
            highlight=True,
            legacy_windows=False
    )
    if detect_legacy_windows():
        console.width = 296
    return console

