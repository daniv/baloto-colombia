# Project : baloto-colombia
# File Name : collection_observer.py
# Dir Path : tests/plugins/pytest_richtrace
# Created on: 2025–06–14 at 18:17:22.
# Package :

from __future__ import annotations

import sys
import time
from collections.abc import Generator
from functools import cached_property
from typing import TYPE_CHECKING

import pluggy
import pytest
from pendulum import DateTime

from baloto.testers.messages import HookMessage
from plugins.pytest_richtrace import NotTest

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any
    from rich.console import Console
    from baloto.core.richer import RichSettings
    from plugins.pytest_richtrace.models import TestRunResults


class CollectionObserver(NotTest):
    name = "richtrace-collection"
    test_run_results: TestRunResults

    def __init__(self, config: pytest.Config, results: TestRunResults):
        self.config = config
        self.test_run_results = results
        self.console: Console | None = None
        self.settings: RichSettings | None = None
        self._starttime: str | None = None
        self.pluginamanager: pytest.PytestPluginManager | None = None
        self.collection = 0
        self.itemcollected = 0

        # TODO: -- experimental
        self.stats: dict[str, list[Any]] = {}
        self._numcollected = 0

    @cached_property
    def isatty(self) -> bool:
        return sys.stdin.isatty()

    @pytest.hookimpl
    def pytest_console_and_settings(self, console: Console, settings: RichSettings) -> None:
        self.settings = settings
        self.console = console

    @pytest.hookimpl
    def pytest_configure(self, config: pytest.Config) -> None:
        self.pluginamanager = config.pluginmanager

    # @pytest.hookimpl(wrapper=True, tryfirst=True)
    def collection_to_consider(self) -> Generator[None]:
        self.log_cli_handler.set_when("collection")

        with catching_logs(self.log_cli_handler, level=self.log_cli_level):
            with catching_logs(self.log_file_handler, level=self.log_file_level):
                return (yield)

    @pytest.hookimpl(tryfirst=True)
    def pytest_collection(self, session: pytest.Session) -> None:
        self.test_run_results.collect.precise_start = time.perf_counter()
        self.test_run_results.collect.start = DateTime.now()
        self._starttime = self.test_run_results.collect.start.to_time_string()
        self.collection += 1
        nodeid = session.nodeid if session.nodeid else None

        hm = HookMessage("pytest_collection")
        if nodeid:
            hm.add_info(nodeid)

        if self.isatty:
            if self.config.option.verbose >= 0:
                self.console.print(hm)
                self.console.print("[b]collecting ... [/]", end="")
                self.console.file.flush()
        elif self.config.option.verbose >= 1:
            self.console.print(hm, end="")
            self.console.print("[b]collecting ... [/]", end="")
            self.console.file.flush()

    # @pytest.hookimpl
    # def pytest_collectstart(self, collector: pytest.Collector) -> None:
    #     is_session = type(collector) is pytest.Session
    #     name = collector.name
    #     is_dir = type(collector) is pytest.Dir
    #     if is_session:
    #         items = collector.items
    #     self.collectstart += 1

    @pytest.hookimpl
    def pytest_make_collect_report(self, collector: pytest.Collector) -> None:
        try:
            self.pluginamanager.hook.pytest_report_make_collect_report(colector=collector)
        except pluggy.HookCallError:
            self.config.pluginmanager.hook.pytest_report_make_collect_report(collector=collector)

    @pytest.hookimpl(tryfirst=True)
    def pytest_ignore_collect(self, collection_path: Path) -> bool | None:
        if collection_path.name.startswith("."):
            return None
        pass


    @pytest.hookimpl
    def pytest_pycollect_makemodule(
        self, module_path: Path, parent: pytest.Collector
    ) -> pytest.Module | None:
        from _pytest.pathlib import import_path

        importmode = self.config.getoption("--import-mode")
        try:
            consider_namespace_packages = self.config.getini("consider_namespace_packages")
            import_path(str(module_path), mode=importmode, root=self.config.rootpath, consider_namespace_packages=consider_namespace_packages)
            # TODO: maybe to publish message?
        except ModuleNotFoundError as exc:
            #TODO: to create this error just maan import to not existing module
            self.test_run_results.collect.count += 1
            self.test_run_results.collect.error[str(module_path)] = exc
            a, b, c = sys.exc_info()
            self.console.print_exception(max_frames=10)
            if not self.config.option.continue_on_collection_errors:
                pytest.exit(exc.msg)
            INDENT = "    "


            # TODO: should be in reporter
            message = exc.msg

            self.console.print(f"{INDENT}[error]Error collecting module[/]:")
            self.console.print(f"{INDENT * 2}[white]{module_path}[/]")
            if message:
                self.console.print(f"{INDENT * 2}{message}")
            return None
        finally:
            return None

    @pytest.hookimpl
    def pytest_pycollect_makeitem(
        self, collector: pytest.Module | pytest.Class, name: str, obj: object
    ) -> pytest.Collector | None:
        pass

    @pytest.hookimpl(tryfirst=True)
    def pytest_collect_file(self, file_path: Path, parent: pytest.Collector) -> pytest.Collector | None:
        if file_path.name.startswith(".") or file_path.suffix is not ".py":
            return None
        pass

    @pytest.hookimpl(trylast=True)
    def pytest_collect_directory(self, path: Path, parent: pytest.Collector) -> pytest.Collector | None:
        if not path.is_dir() or path.name.startswith("."):
            return None
        if path == self.config.rootpath:
            return None
        norecursepatterns = self.config.getini("norecursedirs")
        if path.name in norecursepatterns:
            return None
        pass
        ignore_paths = self.config._getconftest_pathlist(
            "collect_ignore", path=path
        )
        pass
        # ignore_paths = ignore_paths or []
        # excludeopt = config.getoption("ignore")
        # if excludeopt:
        #     ignore_paths.extend(absolutepath(x) for x in excludeopt)
        #
        # if collection_path in ignore_paths:
        #     return True
        #
        # ignore_globs = config._getconftest_pathlist(
        #     "collect_ignore_glob", path=collection_path.parent
        # )
        # ignore_globs = ignore_globs or []
        # excludeglobopt = config.getoption("ignore_glob")
        # if excludeglobopt:
        #     ignore_globs.extend(absolutepath(x) for x in excludeglobopt)
        #
        # if any(fnmatch.fnmatch(str(collection_path), str(glob)) for glob in ignore_globs):
        #     return True
        #
        # allow_in_venv = config.getoption("collect_in_virtualenv")
        # if not allow_in_venv and _in_venv(collection_path):
        #     return True
        #
        # if collection_path.is_dir():
        #     norecursepatterns = config.getini("norecursedirs")
        #     if any(fnmatch_ex(pat, collection_path) for pat in norecursepatterns):
        #         return True


        py_dir = pytest.Dir.from_parent(parent, path=path) # return
        pkginit = path / "__init__.py"
        try:
            has_pkginit = pkginit.is_file()
        except PermissionError:
            # See https://github.com/pytest-dev/pytest/issues/12120#issuecomment-2106349096.
            return None
        if has_pkginit:
            return pytest.Package.from_parent(parent, path=path)
        return None

    @pytest.hookimpl
    def pytest_itemcollected(self, item: pytest.Item) -> None:
        name = item.name
        nodeid = item.nodeid
        self.itemcollected += 1

    @pytest.hookimpl
    def pytest_collectreport(self, report: pytest.CollectReport) -> None:
        longreprtext = report.longreprtext # experimental
        if report.failed:
            self.stats.setdefault("error", []).extend([report])
        elif report.skipped:
            self.stats.setdefault("skipped", []).extend([report])
        items = [x for x in report.result if isinstance(x, pytest.Item)]
        self._numcollected += len(items)
        # if self.isatty:
        #     self.report_collect()
        try:
            self.pluginamanager.hook.pytest_report_collectreport(report=report)
        except pluggy.HookCallError:
            self.config.pluginmanager.hook.pytest_report_collectreport(report=report)
        return None

    @pytest.hookimpl
    def pytest_collection_modifyitems(
        self, session: pytest.Session, config: pytest.Config, items: list[pytest.Item]
    ) -> None:
        pass

    @pytest.hookimpl
    def pytest_deselected(self, items: list[pytest.Item]) -> None:
        pass

    @pytest.hookimpl(trylast=True)
    def pytest_collection_finish(self, session: pytest.Session) -> None:
        pass

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} "
            f"name='{self.name}' "
            f"started={getattr(self, "_starttime", "<UNSET>")}>"
        )