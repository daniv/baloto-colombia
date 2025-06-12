# Project : baloto-colombia
# File Name : reporter.py
# Dir Path : tests/plugins/tracker
# Created on: 2025–06–11 at 14:18:07.

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from rich import box

from rich.padding import Padding
from rich.panel import Panel
from rich.pretty import Pretty
from rich.scope import render_scope
from rich.table import Table
from rich.text import Text
from rich.traceback import PathHighlighter

from baloto.core.rich.testers.messages import HookMessage
from plugins.tracker.header import PytestEnvironment

if TYPE_CHECKING:
    from rich.console import Console
    from rich.console import ConsoleRenderable
    from pendulum import DateTime
    from rich.highlighter import Highlighter
    from plugins.tracker.header import RegisteredPluginInfo
    import _pytest._code as pytest_code

__all__ = ("Reporter",)


INDENT = "    -"


class Reporter:

    def __init__(self, config: pytest.Config, console: Console) -> None:
        self.config = config
        self.console = console

    @property
    def verbosity(self):
        return self.config.option.verbose

    def report_session_start(self, session: pytest.Session, start: DateTime) -> None:
        if self.verbosity > 0:
            datetime_info = f"{start.to_datetime_string()} ({start.timezone_name})"
            hook_message = (
                HookMessage("pytest_sessionstart")
                .add_info(datetime_info)
                .add_key_value("session name", session.name)
            )
            self.console.print(hook_message)

    def report_header(self, env: PytestEnvironment) -> None:
        h = PathHighlighter()
        from rich.columns import Columns

        table = Table(
            box=box.DOUBLE_EDGE,
            show_edge=True,
            style="dim gold1",
            show_header=False,
            highlight=True,
            title="pytest run-time",
            title_justify="center",
        )

        table.add_column("name", style="pytest.keyname")
        table.add_column("value", style="white")
        table.add_row("platform", env.platform)
        table.add_row("python version", env.python)
        if env.pypy:
            table.add_row("pypy version info", env.pypy)

        if env.executable:
            table.add_row("python exec", h(env.executable))
        table.add_row("invocation args", Pretty(list(self.config.invocation_params.args)))
        table.add_row("root path", h(env.rootpath))
        table.add_row("config file", env.configfile)
        if env.cache_dir:
            table.add_row("cachedir", env.cache_dir)

        if env.plugins.registered_plugins:

            def get_content(dist: RegisteredPluginInfo):
                return Text.from_markup(
                    f"[b]{dist.name}[/b]\n[yellow]{dist.version}[/]", justify="center"
                )

            plugins = env.plugins.registered_plugins
            title = env.plugins.registered_title
            plugin_renderables = [Panel(get_content(dist), expand=True) for dist in plugins]
            table.add_section()
            table.add_row(title, Columns(plugin_renderables), end_section=True)

        if env.plugins.active_plugins:
            add_active_plugins(table, env, h)

        scope = render_scope(self.config.inicfg)
        table.add_row("config.inicfg", Padding(scope, (0, 0, 0, len(INDENT))), end_section=True)
        padding = Padding(table, (0, 0, 0, len(INDENT)))
        self.console.print(padding)
        self.console.line(2)
        renderable = render_options_table(config=self.config)
        self.console.print(renderable)

    def report_internalerror(self,             excrepr: pytest_code.code.ExceptionRepr,
            excinfo: pytest.ExceptionInfo[BaseException]):
        tb_style = excrepr.reprtraceback.style
        hook_message = (
            HookMessage("pytest_internalerror")
            .add_key_value("tb-style", tb_style)
            .add_key_value("exc_typename", excinfo.typename, value_color="violet")
            .add_key_value("exc_value", excinfo.typename, value_color="violet")
        )
        self.console.print(hook_message)

        # self._writer.print_key_value("excinfo.typename", value=excinfo.typename, value_color="error")
        # self._writer.print_key_value("excinfo.value", value=str(excinfo.value))
        # path = splitdrive(Path(excrepr.reprcrash.path))
        # self._writer.print_key_value("excrepr.path", value=path, value_color="repr")
        # self._writer.print_key_value("excrepr.lineno", value=str(excrepr.reprcrash.lineno), value_color="repr")
        # self._writer.print_key_value("excrepr.message", value=excrepr.reprcrash.message)
        #



    def _print_key(self, key: str, color: str = "white") -> None:
        self.console.print(f"[{color}]{key}[/]:")


def render_options_table(config: pytest.Config) -> ConsoleRenderable:
    table = Table(
        box=box.HEAVY_EDGE,
        show_edge=True,
        style="dim gold1",
        title="config.options",
        show_header=True,
        highlight=True,
        title_justify="center",
        expand=True,
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
                        Pretty(v, overflow="fold", insert_line=True, highlighter=PathHighlighter())
                    )
                else:
                    row_items.append(Pretty(v, overflow="fold", insert_line=True))
            else:
                row_items.append(str(v))
        table.add_row(*row_items)
        table.add_section()
    return Padding(table, (0, 0, 0, len(INDENT)))


def add_active_plugins(main_table: Table, env: PytestEnvironment, highlighter: Highlighter) -> None:
    table_plugins = Table(show_header=False)
    title = env.plugins.active_title
    for plugin in env.plugins.active_plugins:
        table_plugins.add_row(
            plugin.project_name,
            plugin.pack_or_class,
            highlighter(plugin.location) if plugin.location else "",
        )
    main_table.add_row(title, table_plugins, end_section=True)
