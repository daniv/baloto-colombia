# - Project   : baloto-colombia
# - User Naem : solma
# - File Name : test_errors.py
# - Dir Path  : tests/cleo/exceptions
# - Created on: 2025-05-31 at 14:01:04

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from baloto.cleo.exceptions import ExitStatus
from baloto.cleo.exceptions.errors import CleoError

if TYPE_CHECKING:
    pass

__all__ = ()


@pytest.mark.parametrize("exit_code", [44, None, ExitStatus.INTERNAL_ERROR])
def test_cleo_error_exit_code(exit_code: int | None) -> None:
    message = "A CleoError message"
    cleo_error = CleoError(message)
    cleo_error.exit_code = exit_code

    with pytest.raises(CleoError) as exc_info:
        raise cleo_error

    assert exc_info.typename == CleoError.__name__, "The CleoError.typename was not as expected"
    assert exc_info.value.exit_code == exit_code, "The CleoError.exit_code was not as expected"
    assert exc_info.value.args[0] == message, "The CleoError.message was not as expected"

