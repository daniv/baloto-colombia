# Project : baloto-colombia
# File Name : assertion_error.py
# Dir Path : src/baloto/core/rich/formatters
# Created on: 2025–06–14 at 01:51:18.

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.console import Group

if TYPE_CHECKING:
    from rich.console import ConsoleRenderable
    from pydantic import ValidationError


def validation_error_renderer(error: ValidationError) -> ConsoleRenderable:
    from rich.console import render_scope
    from rich.panel import Panel

    scopes = []
    errors = error.errors(include_url=False)
    for i, err in enumerate(errors, start=1):
        scopes.append(render_scope(err, title=f"error {i}", indent_guides=True))

    return Panel(Group(*scopes), title="ValidationError errors", highlight=True)
