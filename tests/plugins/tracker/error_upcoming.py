# Project : baloto-colombia
# File Name : error_upcoming.py
# Dir Path : tests/plugins/tracker
# Created on: 2025–06–14 at 05:51:56.

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any
from typing import Literal
from typing import TYPE_CHECKING

import pytest


if TYPE_CHECKING:
    from rich.console import Console
    import _pytest._code as pytest_code


class ErrorUpcoming:
    def __init__(self, console: Console) -> None:
        self.console = console
        self.config: pytest.Config | None = None
        self.rich_config: int | None = None

    @pytest.hookimpl(tryfirst=True)
    def pypytest_exception_interact(
        self,
        node: pytest.Item | pytest.Collector,
        call: pytest.CallInfo[Any],
        report: pytest.CollectReport | pytest.TestReport,
    ) -> None:
        from tests.plugins.tracker.assert_report import AssertionErrorReport

        self.console.rule(
            f"[red bold]EXCEPTION INTERACT [dim]({call.excinfo.type})",
            style="red bold",
            align="center",
            characters="=",
        )

        if call.excinfo.type is AssertionError:
            try:
                aer = AssertionErrorReport(node, call, report)
                if aer.report_status:
                    self.console.print(aer)
                renderable = render_exception_info(call.excinfo)
                with self.lock:
                    self.console.print(renderable)

            except* AssertionReportException as e:
                self.console.print_exception()
                pass
        else:
            renderable = render_exception_info(call.excinfo)
            with self.lock:
                self.console.print(renderable)

    @pytest.hookimpl(tryfirst=True)
    def pytest_internalerror(
        self,
        excrepr: pytest_code.code.ExceptionRepr,
        excinfo: pytest.ExceptionInfo[BaseException],
    ) -> bool | None:
        self.console.rule(
            f"[red bold]INTERNAL ERROR [dim]({excinfo.typename})",
            style="red bold",
            align="center",
            characters="=",
        )

        repr_file = Path(excrepr.reprcrash.path).relative_to(self.config.rootpath).as_posix()
        # if settings.tracebacks.isatty_link:
        #     from baloto.core.rich import create_link_markup

            linkname = create_link_markup(excrepr.reprcrash.path, excrepr.reprcrash.lineno)
        else:
            linkname = f"{Path(excrepr.reprcrash.path).as_posix()}:{excrepr.reprcrash.lineno}"
        hook_message = (
            HookMessage("pytest_internalerror")
            .add_info(excinfo.typename)
            .add_key_value("reprcrash.lineno", str(excrepr.reprcrash.lineno), value_color="repr")
            .add_key_value("reprcrash.message", str(excrepr.reprcrash.message))
            .add_key_value("reprcrash.path", repr_file, value_color="none")
            .add_key_value("location", linkname, value_color="none", escape_markup=False)
            .add_key_value("reprtraceback.style", excrepr.reprtraceback.style)
            .add_key_value("showing locals", str(self.config.option.showlocals), value_color="none")
        )
        self.console.print(hook_message)
        return self.reporter.rich_internalerror(excrepr, excinfo)

    def pytest_warning_recorded(
        self,
        warning_message: warnings.WarningMessage,
        when: Literal["config", "collect", "runtest"],
        nodeid: str,
        location: tuple[str, int, str] | None,
    ) -> None: ...
