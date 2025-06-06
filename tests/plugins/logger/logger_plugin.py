# — Project : baloto-colombia
# — File Name : logger_plugin.py
# — Dir Path : tests/plugins/logger
# — Created on: 2025–06–04 at 20:06:59.

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from pydantic import BaseModel, ConfigDict, PrivateAttr
from rich import Console

if TYPE_CHECKING:
    pass

__all__ = ("LoggerPlugin", )


class LoggerPlugin:

    name: str = "logger-plugin"
    def __init__(self) -> None:

        self.config: pytest.Config | None = PrivateAttr(default=None)
        self.console: Console


        # console = ConsoleFactory.console_output()

        # formatter = ConsoleFormatter(
        #     #     rich_tracebacks=rich_tracebacks
        #     # )
        #     # handler.setFormatter(formatter)
        #     # if not io.is_very_verbose():
        #     #     handler.addFilter(POETRY_FILTER)
        #
        #     # FORMAT = "%(asctime)-15s - %(levelname)s - %(message)s"

        #
        #     from time import sleep
        #
        #     log = logging.getLogger("conftest")
        #     log.info("Server starting...")
        #
        #     log.info("Listening on http://127.0.0.1:8080")
        #     # sleep(1)
        #
        #     log.info("GET /index.html 200 1298")
        #     log.info("GET /imgs/backgrounds/back1.jpg 200 54386")
        #     log.info("GET /css/styles.css 200 54386")
        #     log.warning("GET /favicon.ico 404 242")
        #     # sleep(1)
        #
        #     log.debug(
        #         "JSONRPC request\n--> %r\n<-- %r",
        #         {
        #             "version": "1.1",
        #             "method": "confirmFruitPurchase",
        #             "params": [["apple", "orange", "mangoes", "pomelo"], 1.123],
        #             "id": "194521489",
        #         },
        #         {"version": "1.1", "result": True, "error": None, "id": "194521489"},
        #     )
        #     log.debug(
        #         "Loading configuration file /adasd/asdasd/qeqwe/qwrqwrqwr/sdgsdgsdg/werwerwer/dfgerert/ertertert/ertetert/werwerwer"
        #     )
        #     log.error("Unable to find 'pomelo' in database!")
        #     log.info("POST /jsonrpc/ 200 65532")
        #     log.info("POST /admin/ 401 42234")
        #     log.warning("password was rejected for admin site.")
        #
        #     def divide() -> None:
        #         number = 1
        #         divisor = 0
        #         foos = ["foo"] * 100
        #         log.debug("in divide")
        #         try:
        #             number / divisor
        #         except:
        #             log.exception("An error of some kind occurred!")
        #
        #     divide()
        #     sleep(1)
        #     log.critical("Out of memory!")
        #     log.info("Server exited with code=-1")
        #     log.info("[bold]EXITING...[/bold]", extra=dict(markup=True))
        #     i = 0



