# Project : baloto-colombia
# File Name : plugin.py
# Dir Path : tests/plugins/pytest_richtrace
# Created on: 2025–06–14 at 14:28:38.
# Package :

from __future__ import annotations

import threading
import warnings
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING

import pluggy
import pytest
from rich.panel import Panel
from rich.text import Text


from plugins.pytest_richtrace.models import TestRunResults
from plugins.pytest_richtrace import cleanup_factory
from baloto.cleo.io.outputs.output import Verbosity

if TYPE_CHECKING:
    from typing import Any
    from typing import Literal
    from _pytest._code import code as pytest_code
    from plugins.pytest_richtrace import PytestPlugin
    from baloto.core.richer import RichSettings
    from rich.console import Console

PLUGIN_NAME = "pytest-richtrace-plugin"


@pytest.hookimpl
def pytest_addhooks(pluginmanager: pytest.PytestPluginManager) -> None:
    from tests.plugins.pytest_richtrace.hookspecs import ReportingHookSpecs

    pluginmanager.add_hookspecs(ReportingHookSpecs)


@pytest.hookimpl
def pytest_addoption(parser: pytest.Parser, pluginmanager: pytest.PytestPluginManager) -> None:
    pass


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config: pytest.Config) -> None:
    from baloto.core.richer import ConsoleFactory
    from baloto.core.richer import get_rich_settings

    console = ConsoleFactory.console_output()
    config.pluginmanager.hook.pytest_console_and_settings.call_historic(
        kwargs=dict(console=console, settings=get_rich_settings())
    )

    # tracker_plugin = PytestRichTrace(config)
    # config.pluginmanager.register(tracker_plugin, PytestRichTrace.name)


@pytest.hookimpl
def pytest_plugin_registered(
    plugin: PytestPlugin, plugin_name: str, manager: pytest.PytestPluginManager
) -> None:
    pass
    if plugin_name in ["terminalreporter"]:
        if hasattr(plugin, "name"):
            if getattr(plugin, "name", None) == PytestRichTrace.name:
                return

        config = getattr(plugin, "config")
        # TODO: after richtrace implemented
        # tracker_plugin = PytestRichTrace(config)
        # manager.unregister(plugin, "terminalreporter")
        # manager.register(tracker_plugin, PytestRichTrace.name)
        tracker_plugin = PytestRichTrace(config)
        config.pluginmanager.register(tracker_plugin, tracker_plugin.name)
        # config.pluginmanager.register(tracker_plugin, "terminalreporter")


def pytest_exception_interact(
    node: pytest.Item | pytest.Collector,
    call: pytest.CallInfo[Any],
    report: pytest.CollectReport | pytest.TestReport,
) -> None:
    pass


@pytest.hookimpl
def pytest_internalerror(
    excrepr: pytest_code.ExceptionRepr,
    excinfo: pytest.ExceptionInfo[BaseException],
) -> bool | None:
    pass


@pytest.hookimpl
def pytest_keyboard_interrupt(
    excinfo: pytest.ExceptionInfo[KeyboardInterrupt | pytest.Exit],
) -> None:
    pass


@pytest.hookimpl
def pytest_warning_recorded(
    warning_message: warnings.WarningMessage,
    when: Literal["config", "collect", "runtest"],
    nodeid: str,
    location: tuple[str, int, str] | None,
) -> None:
    pass


@pytest.hookimpl
def pytest_unconfigure(config: pytest.Config) -> None:
    if config.pluginmanager.hasplugin(PytestRichTrace.name):
        plugin = config.pluginmanager.get_plugin(PytestRichTrace.name)
        config.pluginmanager.unregister(plugin, PytestRichTrace.name)


@pytest.mark.optionalhook
def pytest_testnodedown(node):
    # deal with xdist
    pass
    # if hasattr(node, 'slaveoutput'):
    #     node.config._json_environment = node.slaveoutput['json_environment']


class PytestRichTrace(pytest.TerminalReporter):

    name: str = "pytest-richtrace"

    def __init__(self, config: pytest.Config) -> None:
        # TODO: will removes after full integration
        super().__init__(config)
        self.config = config
        self.console: Console | None = None
        self._lock = threading.Lock()
        self.settings: RichSettings | None = None
        self.test_results: TestRunResults | None = None
        self.hook_caller: pluggy.HookRelay | None = None
        self._starttime: str | None = None

    @property
    def verbosity(self) -> Verbosity:
        return self.settings.verbosity

    @property
    def no_header(self) -> bool:
        return bool(self.config.option.no_header)

    @property
    def showheader(self) -> bool:
        return self.verbosity >= Verbosity.NORMAL

    @pytest.hookimpl(tryfirst=True)
    def pytest_configure(self, config: pytest.Config) -> None:
        from plugins.pytest_richtrace.error_observer import ErrorExecutionObserver
        from plugins.pytest_richtrace.collection_observer import CollectionObserver
        from plugins.pytest_richtrace.test_execution_observer import TestExecutionObserver

        pluginmanager = config.pluginmanager
        self.hook_caller = pluginmanager.hook
        self.test_results = TestRunResults()

        from plugins.pytest_richtrace.rich_reporter import RichReporter

        reporter = RichReporter(config)
        reporter.monitored_classes.extend(
            [
                ErrorExecutionObserver.name,
                CollectionObserver.name,
                TestExecutionObserver.name,
                PLUGIN_NAME,
                self.name,
            ]
        )
        pluginmanager.register(reporter, name=RichReporter.name)
        config.add_cleanup(cleanup_factory(pluginmanager, reporter))

        errors = ErrorExecutionObserver(config, self.test_results)
        pluginmanager.register(errors, name=ErrorExecutionObserver.name)
        config.add_cleanup(cleanup_factory(pluginmanager, errors))
        reporter.monitored_classes.append(errors.name)

        collector = CollectionObserver(config, self.test_results)
        pluginmanager.register(collector, name=CollectionObserver.name)
        config.add_cleanup(cleanup_factory(pluginmanager, collector))

        runtest = TestExecutionObserver(config, self.test_results)
        pluginmanager.register(runtest, name=TestExecutionObserver.name)
        config.add_cleanup(cleanup_factory(pluginmanager, runtest))

    def pytest_console_and_settings(self, console: Console, settings: RichSettings) -> None:
        self.settings = settings
        self.console = console
        from tests.plugins import __version__
        panel = Panel(
            Text(
                "A pytest plugin using Rich for beautiful test result formatting.",  # noqa: E501
                justify="center",
            ),
            style="bold green",
            padding=2,
            title="pytest-rich-trace",
            subtitle=f"v{__version__}",
        )
        console.print(panel)

    @pytest.hookimpl(trylast=True)
    def pytest_sessionstart(self, session: pytest.Session) -> None:
        import time
        from pydantic_extra_types.pendulum_dt import DateTime

        self.test_results.precise_start = time.perf_counter()
        self.test_results.start = DateTime.now()
        self._starttime = self.test_results.start.to_time_string()

        session.name = "Baloto UnitTesting"


        # TODO: remove after fully override
        setattr(self, "_session", session)
        from _pytest import timing
        setattr(self, "_session_start", timing.Instant())

        if not self.showheader:
            return
        self.console.rule(f"Session '{session.name}' starts", characters="=")

        if not self.no_header:
            self._collector_services()
            environment_data = self.hook_caller.pytest_collect_env_info(config=session.config)
            self._collector_services(do_register=False)
            self.hook_caller.pytest_render_header(config=session.config, data=environment_data)


    def _collector_services(self, do_register=True) -> None:
        from tests.plugins.pytest_richtrace.services.collector_services import (
            PytestCollectorService,
            CollectorWrapper,
            PluggyCollectorService,
            PoetryCollectorService,
            PythonCollectorService,
            HookHeaderCollectorService,
        )
        from tests.plugins.pytest_richtrace.rich_reporter import RichReporter

        pluginmanager = self.config.pluginmanager
        names = [
            PytestCollectorService.name,
            PluggyCollectorService.name,
            PoetryCollectorService.name,
            PythonCollectorService.name,
            HookHeaderCollectorService.name,
            CollectorWrapper.name,
        ]
        if do_register:
            plugin = pluginmanager.get_plugin(RichReporter.name)
            plugin.monitored_classes.extend(names)

            collector_wrapper = CollectorWrapper()
            pluginmanager.register(collector_wrapper, CollectorWrapper.name)

            python_collector = PythonCollectorService()
            pluginmanager.register(python_collector, PythonCollectorService.name)

            pytest_collector = PytestCollectorService()
            pluginmanager.register(pytest_collector, PytestCollectorService.name)

            poetry_collector = PoetryCollectorService()
            pluginmanager.register(poetry_collector, PoetryCollectorService.name)

            pluggy_collector = PluggyCollectorService()
            pluginmanager.register(pluggy_collector, PluggyCollectorService.name)

            hook_collector = HookHeaderCollectorService()
            pluginmanager.register(hook_collector, HookHeaderCollectorService.name)
        else:
            for name in names:
                if pluginmanager.hasplugin(name):
                    pluginmanager.unregister(pluginmanager.get_plugin(name), name)

    #
    #
    #
    #     self.reporter.report_session_start(session, self.test_results.start)
    #
    #     from tests.plugins.tracker.header import build_environment
    #
    #     environment = build_environment(config=self.config)
    #     if not self.no_header:
    #         self.reporter.report_header(environment)
    #

    def write_fspath_result(self, nodeid: str, res: str, **markup: bool) -> None:
        pass

    def write_ensure_prefix(self, prefix: str, extra: str = "", **kwargs) -> None:
        pass

    def ensure_newline(self) -> None:
        pass

    def wrap_write(
        self,
        content: str,
        *,
        flush: bool = False,
        margin: int = 8,
        line_sep: str = "\n",
        **markup: bool,
    ) -> None:
        pass

    def write_line(self, line: str | bytes, **markup: bool) -> None:
        pass

    def write(self, content: str, *, flush: bool = False, **markup: bool) -> None:
        pass

    def flush(self) -> None:
        pass

    # TODO: This section is temporary overriding the pytest terminal methods and prevent writing to console
    def rewrite(self, line: str, **markup: bool) -> None:
        from rich.control import Control

        pass

        if line == "temporary-bypass":
            from rich.segment import ControlType

            self.console.control(Control((ControlType.ERASE_IN_LINE, 2)))
            self.console.control(Control((ControlType.CURSOR_MOVE_TO_COLUMN, 0)))
            self.console.file.write(line)
        return None

    def section(self, title: str, sep: str = "=", **kw: bool) -> None:
        pass

    def line(self, msg: str, **kw: bool) -> None:
        pass

    def _write_report_lines_from_hooks(self, lines: Sequence[str | Sequence[str]]) -> None:
        return None

    def pytest_collection(self) -> None:
        pass

    def pytest_collectreport(self, report: pytest.CollectReport) -> None:
        pass

    def pytest_collection_finish(self, session: pytest.Session) -> None:
        pass

    def pytest_deselected(self, items: Sequence[pytest.Item]) -> None:
        pass

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} "
            f"name='{self.name}' "
            f"verbosity={self.verbosity!r} "
            f"started={getattr(self, "_starttime", "<UNSET>")}>"
        )
