# - Project   : baloto-colombia
# - User Naem : solma
# - File Name : test_errors.py
# - Dir Path  : tests/cleo/exceptions
# - Created on: 2025-05-31 at 14:01:04

from __future__ import annotations

import pytest
from hamcrest import assert_that
from hamcrest import equal_to

from baloto.cleo.exceptions import ExitStatus
from baloto.cleo.exceptions.errors import CleoError


@pytest.mark.parametrize("exit_code", [44, None, ExitStatus.INTERNAL_ERROR])
def test_cleo_error_exit_code(exit_code: int | None) -> None:
    message = "A CleoError message"
    cleo_error = CleoError(message)
    cleo_error.exit_code = exit_code

    with pytest.raises(CleoError) as exc_info:
        raise cleo_error

    assert_that(exc_info.type, equal_to(type(CleoError).__name__), "typename")
    assert_that(exc_info.value.exit_code, equal_to(exit_code), "exit_code")
    assert_that(exc_info.value.args[0], equal_to(message), "exit_code")
