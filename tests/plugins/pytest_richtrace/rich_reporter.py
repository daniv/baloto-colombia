# Project : baloto-colombia
# File Name : rich_reporter.py
# Dir Path : tests/plugins/pytest_richtrace
# Created on: 2025–06–14 at 19:52:06.
# Package :

from __future__ import annotations

import textwrap
from pathlib import Path
from typing import ClassVar
from typing import TYPE_CHECKING

import pytest
import rich
import rich.box
# import rich.console
import rich.padding
import rich.panel
import rich.table
import rich.pretty
# import rich.theme
import rich.traceback
import rich.highlighter
import rich.text
import rich.columns

from baloto.cleo.io.outputs.output import Verbosity
from baloto.testers.messages import HookMessage
from plugins.pytest_richtrace import NotTest

if TYPE_CHECKING:
    from rich.console import ConsoleRenderable
    from rich.console import Console
    from baloto.core.richer import RichSettings
    from plugins.pytest_richtrace import PytestPlugin
    from collections import ChainMap


INDENT = "    "

class RichReporter(NotTest):
    name = "richtrace-reporter"

    monitored_classes: ClassVar[list[str]] = []

    def __init__(self, config: pytest.Config):
        self.config = config
        self.console: Console | None = None
        self.settings: RichSettings | None = None

    @property
    def traceconfig(self) -> bool:
        return self.config.option.traceconfig

    @property
    def verbosity(self) -> Verbosity:
        if self.settings is None:
            return Verbosity.QUIET
        return self.settings.verbosity

    @pytest.hookimpl(tryfirst=True)
    def pytest_console_and_settings(self, console: Console, settings: RichSettings) -> None:
        self.settings = settings
        self.console = console

    @pytest.hookimpl
    def pytest_configure(self, config: pytest.Config) -> None:
        pass

    @pytest.hookimpl(trylast=True)
    def pytest_plugin_registered(self, plugin: PytestPlugin, plugin_name: str) -> None:
        if plugin_name is None or self.verbosity < Verbosity.NORMAL:
            return None

        if self.config.option.traceconfig:
            hm = HookMessage("pytest_plugin_registered").add_info(plugin_name)
            self.console.print(hm)
        else:
            if plugin_name in self.monitored_classes:
                hm = HookMessage("pytest_plugin_registered").add_info(plugin_name)
                self.console.print(hm)
        return None

    @pytest.hookimpl
    def pytest_render_header(self, config: pytest.Config, data: ChainMap) -> bool:


        pathh = rich.traceback.PathHighlighter()
        reprh = rich.highlighter.ReprHighlighter()

        table = rich.table.Table(
            box=rich.box.DOUBLE_EDGE,
            show_edge=True,
            style="dim gold1",
            border_style="dim",
            show_header=False,
            expand=True,
            highlight=True,
            title="pytest/python run-time information",
            title_justify="center",
        )
        table.add_column("name", style="pytest.keyname")
        table.add_column("value", style="white")

        for key_name in data.fromkeys(
            [
                "platform",
                "python",
                "python_ver_info",
                "pypy",
                "executable",
                "pytest_ver",
                "rootdir",
                "configfile",
                "cachedir",
                "invocation_params",
                "plugins",
                "poetry_version",
                "project_version",
                "packages",
            ]
        ):

            if data.get(key_name) is None:
                continue

            value = data.get(key_name)
            match key_name:
                case "rootdir" | "configfile" | "cachedir":
                    if key_name == "rootdir":
                        table.add_section()
                    table.add_row(key_name, pathh(value))
                case "invocation_params":
                    table.add_row("invocation parameters", f"[green]{value}[/]")
                case "python":
                    table.add_row("python version", reprh(value))
                case "pytest_ver":
                    table.add_row("pytest version", reprh(value))
                case "python_ver_info":
                    table.add_row("python version info", reprh(value))
                case "plugins":
                    table.add_row("pluggy version", value.get("pluggy_version"))
                    if value.get("dist_info"):
                        renderable = render_registered_plugins(
                            value.get("dist_title", "registered plugins"),
                            value.get("dist_info"),
                            self.traceconfig,
                        )
                        end_section = False if self.traceconfig else True
                        table.add_row("registered plugins", renderable, end_section=end_section)
                    if self.traceconfig:
                        renderable = render_active_plugins(
                            value.get("name_title", "active plugins"), value.get("names_info")
                        )
                        table.add_row("active plugins", renderable, end_section=True)
                case "executable":
                    if (
                        self.verbosity > Verbosity.NORMAL
                        or self.config.option.debug
                        or getattr(self.config.option, "pastebin", None)
                    ):
                        table.add_row(key_name, pathh(value))
                case "poetry_version" | "project_version":  # packages
                    table.add_row(key_name.replace("_", " "), value)
                case "packages":
                    if self.traceconfig or self.config.option.show_packages:
                        renderable = render_packages(value)
                        table.add_row("packages versions", renderable)
                case _:
                    table.add_row(key_name, value)

        from rich.scope import render_scope
        from rich.console import Group

        panel = rich.panel.Panel.fit(
            Group(table, render_options_table(config), render_scope(self.config.inicfg)),
            title="[command]config.option and [command]config.inicfg[/]",
            border_style="bright_yellow",
            padding=(0, 1),
        )
        self.console.print(rich.padding.Padding(panel, (0, 0, 0, 8)), new_line_start=True, justify="center")
        return True

    @pytest.hookimpl
    def pytest_report_collectreport(self, report: pytest.CollectReport) -> None:
        if self.verbosity > Verbosity.NORMAL and report.nodeid:
            hm = HookMessage("pytest_report_collectreport").add_info(report.nodeid or "")
            self.console.print(hm)
            if self.verbosity > Verbosity.VERBOSE and report.nodeid:
                # print_key_value(self.console, "nodeid", report.nodeid, prefix=INDENT)
                table = rich.table.Table(show_header=False, show_edge=False, show_lines=False)
                table.add_column("name", style="pytest.keyname", width=15)
                table.add_column("value", width=61)

                table.add_row("outcome", f"[{report.outcome}]{report.outcome}[/]")
                if report.caplog:
                    table.add_row(
                        "caplog",
                        strip_escape_from_string(report.caplog),
                    )

                if report.capstderr:
                    table.add_row(
                        "capstderr",
                        strip_escape_from_string(report.capstderr),
                    )

                if report.capstdout:
                    width = self.console.width - len(INDENT) * 3
                    stdout_text = "\n".join(
                        textwrap.wrap(
                            strip_escape_from_string(report.capstdout),
                            width=width,
                            initial_indent=INDENT * 2,
                            subsequent_indent=INDENT * 2,
                        )
                    ).strip()
                    table.add_row("capstdout", stdout_text)

                padding = rich.padding.Padding(table, (0, 0, 0, 8))
                try:
                    self.console.print(padding)
                except (Exception, TypeError) as err:
                    pass

        return None

    @pytest.hookimpl
    def pytest_report_make_collect_report(self, collector: pytest.Collector) -> None:
        if self.verbosity > Verbosity.NORMAL:
            if isinstance(collector, (pytest.Session, pytest.Directory)):
                hm = HookMessage("pytest_make_collect_report").add_info(f"[i]{collector.nodeid}[/]")
            elif isinstance(collector, pytest.File):
                # TODO: bug here print to the left no indent
                hm = HookMessage("pytest_make_collect_report").add_info(f"[i]{collector.nodeid}[/]")
            else:
                raise NotImplementedError

            self.console.print(hm)
        return None


    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} " f"name='{self.name}'>"


def render_packages(packages: list[dict[str, str]]) -> ConsoleRenderable:
    table = _get_plugins_table("")
    table.title = "available packages [dim]([red]*red[/] means outdated)[/]"
    table.caption = None
    table.title_style = "gold1"
    table.title_justify = "center"
    for package in packages:
        table.add_row(
            f"[cyan]{package["name"]}[/]",
            f"[bright_green]{package["current_ver"]}[/]",
            f"{package["latest_ver"]}",
            f"[white]{package["summary"]}[/]",
        )
    return table


def render_registered_plugins(title, dists: list[dict[str, str]], trace: bool) -> ConsoleRenderable:
    ph = rich.traceback.PathHighlighter()

    if trace:
        table = _get_plugins_table(title)
        for d in dists:
            p = Path(d.get("plugin"))
            pack = f"{p.parts[0]}~{p.parent.name}/{p.name}"
            table.add_row(
                f"[bright_white]{d.get("name")}[/]",
                f"[yellow]{d.get("version")}[/]",
                ph(pack),
                d.get("summary"),
            )
        return table

    def get_content(dist_info: dict[str, str]):
        return rich.text.Text.from_markup(
            f"[b]{dist_info['name']}[/b]\n[yellow]{dist_info['version']}[/]", justify="center"
        )

    plugin_renderables = [rich.panel.Panel(get_content(dist), expand=True) for dist in dists]
    return rich.columns.Columns(plugin_renderables, title=title)


def render_active_plugins(title, plugins: list[dict[str, str]]) -> ConsoleRenderable:
    import textwrap

    ph = rich.traceback.PathHighlighter()

    table = _get_plugins_table(title)
    for plugin in plugins:
        p = Path(plugin.get("plugin"))
        if p.is_file():
            path = f"{p.parts[0]}~{p.parent.name}/{p.name}"
            table.add_row(f"[bright_white]{plugin.get("name")}[/]", ph(path))
        else:
            repr_ = textwrap.shorten(plugin.get("plugin"), width=111)
            table.add_row(
                f"[bright_white]{plugin.get("name")}[/]", f"[bright_magenta dim]{repr_}[/]"
            )
    return table


def render_options_table(config: pytest.Config) -> ConsoleRenderable:
    table = rich.table.Table(
        box=rich.box.DOUBLE_EDGE,
        show_header=True,
        highlight=True,
        expand=True,
        style="dim gold1",
        border_style="dim",
    )
    item_count = 3
    for col in range(item_count * 2):
        if col % 2 == 0:
            name = "option"
        else:
            name = "value"
        table.add_column(name, header_style="green")

    def chunk(lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i : i + n]  # noqa

    options = vars(config.option)
    keys = sorted(options.keys())
    rows_of_keys = chunk(keys, item_count)
    for row in rows_of_keys:
        row_items = []
        for key in row:
            row_items.append(key)
            v = options[key]
            if isinstance(v, str):
                row_items.append(f'"{v}"')
            if isinstance(v, list):
                if key == "file_or_dir":
                    row_items.append(
                        rich.pretty.Pretty(v, overflow="fold", insert_line=True, highlighter=rich.traceback.PathHighlighter())
                    )
                else:
                    row_items.append(rich.pretty.Pretty(v, overflow="fold", insert_line=True))
            else:
                row_items.append(str(v))
        table.add_row(*row_items)
        table.add_section()
    return table


def _get_plugins_table(caption: str):
    return rich.table.Table(
        show_header=False,
        box=rich.box.SQUARE_DOUBLE_HEAD,
        title_justify="right",
        border_style="dim b",
        caption=caption,
        caption_style="gold1",
        expand=True,
    )
