# - Project   : baloto-colombia
# - User Naem : solma
# - File Name : conftest.py
# - Dir Path  : tests/cleo/io
# - Created on: 2025-05-30 at 11:44:32

from __future__ import annotations

from typing import TYPE_CHECKING, Generator, Callable

import pytest

if TYPE_CHECKING:
    from baloto.cleo.exceptions.errors import CleoLogicError
    from baloto.cleo.exceptions import ExitStatus

# Generator[YieldType, SendType, ReturnType]


@pytest.fixture(scope="function")
def assert_cleo_logic_error() -> Generator[Callable[[CleoLogicError, ...], None], ..., None]:
    def _validate_error(
        exc: CleoLogicError,
        *,
        message: str | None,
        code: str | None,
        exit_code: ExitStatus | None = None,
        len_notes: int | None = None,
    ) -> None:
        if message:
            assert exc.message == message, "The exc.message was not as expected"
        if code:
            assert exc.code == code, "The exc.code was not as expected"
        if exit_code:
            assert exc.exit_code == exit_code, "The exc.exit_code was not as expected"
        if len_notes:
            assert len(exc.__notes__) == len_notes, "The length of exc.__notes__ was not as expected"

    yield _validate_error
