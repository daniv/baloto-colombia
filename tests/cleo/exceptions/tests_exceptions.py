from __future__ import annotations

from typing import TYPE_CHECKING, Type

import pytest
from pydantic import ValidationError
from pytest import param

from baloto.cleo.exceptions import ExitStatus
from baloto.cleo.exceptions.errors import CleoError, CleoLogicError, CleoRuntimeError

if TYPE_CHECKING:
    from baloto.cleo.exceptions import ExitStatus, CleoErrorCodes


@pytest.mark.parametrize("exit_code", [44, None, ExitStatus.INTERNAL_ERROR])
def cleo_error_exit_code_test(exit_code: int | None) -> None:
    message = "A CleoError message"
    cleo_error = CleoError(message)
    cleo_error.exit_code = exit_code

    with pytest.raises(CleoError) as exc_info:
        raise cleo_error

    assert exc_info.typename == CleoError.__name__, "The CleoError.typename was not as expected"
    assert exc_info.value.exit_code == exit_code, "The CleoError.exit_code was not as expected"
    assert exc_info.value.args[0] == message, "The CleoError.message was not as expected"


@pytest.mark.parametrize("code", ["validator-argument-default-value", None])
def cleo_logic_error_test(code: CleoErrorCodes | None) -> None:
    message = "A CleoLogicError message"
    cleo_logic_error = CleoLogicError(message, code=code)

    with pytest.raises(CleoError) as exc_info:
        raise cleo_logic_error

    assert exc_info.typename == CleoLogicError.__name__, "The CleoLogicError.typename was not as expected"
    assert exc_info.value.exit_code == ExitStatus.USAGE_ERROR, "The CleoLogicError.exit_code was not as expected"
    assert getattr(exc_info.value, "code") == code, "The CleoLogicError.code was not as expected"
    assert exc_info.value.args[0] == message, "The CleoLogicError.message was not as expected"
    assert len(exc_info.value.__notes__) > 0, "The 'CleoLogicError.__notes__ was not as expected"
    if code:
        assert str(exc_info.value).strip() == f"{message} {code}", "The 'CleoLogicError.__str__' message was not as expected"
    else:
        assert str(exc_info.value).strip() == message, "The 'CleoLogicError.__str__' message was not as expected"


def cleo_runtime_error_test() -> None:
    message = "A CleoRuntimeError message"
    cleo_logic_error = CleoRuntimeError(message)

    with pytest.raises(CleoRuntimeError) as exc_info:
        raise cleo_logic_error

    assert exc_info.typename == CleoRuntimeError.__name__, "The CleoRuntimeError.typename was not as expected"
    assert exc_info.value.exit_code == ExitStatus.INTERNAL_ERROR, "The CleoRuntimeError.exit_code was not as expected"
    assert exc_info.value.args[0] == message, "The CleoRuntimeError.message was not as expected"
    assert len(exc_info.value.__notes__) > 0, "The CleoRuntimeError.__notes__ was not as expected"


# noinspection PyArgumentList
@pytest.mark.parametrize(
    "exc, msg, code",
    [
        param(CleoLogicError, None, 3, id="cle-types"),
        param(CleoLogicError, None, None, id="cle-all-none"),
        param(CleoLogicError, "msg", "invalid", id="cle-inv-code"),
        param(CleoLogicError, None, "cmd-invalid-option", id="no-msg"),
    ],
)
def cleo_raise_validation_error_test(request: pytest.FixtureRequest, exc: Type[Exception], msg: str | None, code: CleoErrorCodes | None) -> None:
    p_id = request.node.callspec.id
    error_count = 1
    error_types = ["string_type"]
    error_msgs = ["Input should be a valid string"]

    match p_id:
        case "cle-types":
            error_count = 2
            error_types.append("literal_error")
            error_msgs.append("Input should be")
        case "cle-all-none":
            ...
        case "cle-inv-code":
            error_types = ["literal_error"]
            error_msgs = ["Input should be"]

    with pytest.raises(ValidationError) as exc_info:
        exc(msg, code=code)

    ve = exc_info.value
    errors = exc_info.value.errors(include_url=False, include_context=False, include_input=False)

    assert ve.error_count() == error_count, "The error.error_count() was not as expected"
    for idx, error in enumerate(errors):
        assert error.get("type") == error_types[idx], f"The error[{idx}].type was not as expected"
        assert error.get("msg").startswith(error_msgs[idx]), f"The error[{idx}].msg was not as expected"
