# Project : baloto-colombia
# File Name : messages.py
# Dir Path : tests/rich
# Created on: 2025–06–12 at 15:31:10.

from __future__ import annotations

from typing import LiteralString
from typing import Sized
from typing import TYPE_CHECKING
from typing import TypeVar
from typing import cast

import pytest
from hamcrest import is_not
from hamcrest import none
from pydantic import ValidationError
from pytest import param
from pytest import raises
from hamcrest import assert_that
from hamcrest import equal_to
from hamcrest import has_length

if TYPE_CHECKING:
    from baloto.cleo.io.buffered_io import BufferedIO
    from baloto.cleo.io.stream_io import StreamIO
    from _pytest.fixtures import SubRequest

parameterize = pytest.mark.parametrize

SizedT = TypeVar("SizedT", bound=Sized)

@pytest.fixture(scope='function')
def hook_message_func():
    return HookMessage("pytest_sessionstart")

@pytest.fixture(scope='module')
def hook_message_mod():
    HookMessage("pytest_sessionstart")

def test_basic_message(buffered_io: BufferedIO, stream_io: StreamIO | None, hook_message_func: HookMessage) -> None:
    assert_that(hook_message_func.hookname, equal_to("pytest_sessionstart"), "hook_name")
    assert_that(hook_message_func.prefix, equal_to(MessagePrefixEnum.PREFIX_SQUARE), "prefix")
    assert_that(hook_message_func.info, equal_to(""), "info")
    assert_that(cast(SizedT, hook_message_func.key_values), has_length(0), "key_values")
    if stream_io:
        stream_io.output.line()
        stream_io.output.write(hook_message_func, new_line_start=True)

def test_info(buffered_io: BufferedIO, stream_io: StreamIO, hook_message_func: HookMessage) -> None:
    hook_message_func.add_info("An info topic")
    assert_that(hook_message_func.info, equal_to("An info topic"), "info")
    if stream_io:
        stream_io.output.line()
        stream_io.output.write(hook_message_func, new_line_start=True)

@parameterize("render_as", ["plain", "markup"])
@parameterize(
    "info",
    [
        param("\x1b[1;38;5;76mThis is an ansi message.\x1b[0m", id="ansi"),
        param("[blue]This is a [yellow]markup[/] message.[/]", id="markup"),
        param("This is a plain message.", id="plain"),
    ]
)
def test_info_with_markup(request: SubRequest, buffered_io: BufferedIO, stream_io: StreamIO, hook_message_func: HookMessage, info: str, render_as: RenderType) -> None:
    expected = "This is {type} message."

    param_id = request.node.callspec.id
    hook_message_func.add_info(info, render_as=render_as)
    if "ansi-" in param_id:
        assert_that(hook_message_func.info, equal_to(expected.format(type="an ansi")), "info")
        assert_that(hook_message_func._info_markup, none(), "_info_markup")
    elif "markup-" in param_id:
        assert_that(hook_message_func.info, equal_to(expected.format(type="a markup")), "info")
        if render_as == "markup":
            assert_that(hook_message_func._info_markup, is_not(none()), "_info_markup")
        else:
            assert_that(hook_message_func._info_markup, none(), "_info_markup")
    else:
        assert_that(hook_message_func.info, equal_to(expected.format(type="a plain")), "info")
        if render_as == "plain":
            assert_that(hook_message_func._info_markup, none(), "_info_markup")
        else:
            assert_that(hook_message_func._info_markup, is_not(none()), "_info_markup")

    if stream_io:
        stream_io.output.line()
        stream_io.output.write(hook_message_func, new_line_start=True)

    # assert_that(hook_message_func.info, equal_to("An info topic"), "info")

