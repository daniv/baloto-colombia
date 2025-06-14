"""
PydanticErrorCodes = Literal[
    'class-not-fully-defined',
    'custom-json-schema',
    'decorator-missing-field',
    'discriminator-no-field',
    'discriminator-alias-type',
    'discriminator-needs-literal',
    'discriminator-alias',
    'discriminator-validator',
    'callable-discriminator-no-tag',
    'typed-dict-version',
    'model-field-overridden',
    'model-field-missing-annotation',
    'config-both',
    'removed-kwargs',
    'circular-reference-schema',
    'invalid-for-json-schema',
    'json-schema-already-used',
    'base-model-instantiated',
    'undefined-annotation',
    'schema-for-unknown-type',
    'import-error',
    'create-model-field-definitions',
    'validator-no-fields',
    'validator-invalid-fields',
    'validator-instance-method',
    'validator-input-type',
    'root-validator-pre-skip',
    'model-serializer-instance-method',
    'validator-field-config-info',
    'validator-v1-signature',
    'validator-signature',
    'field-serializer-signature',
    'model-serializer-signature',
    'multiple-field-serializers',
    'invalid-annotated-type',
    'type-adapter-config-unused',
    'root-model-extra',
    'unevaluable-type-annotation',
    'dataclass-init-false-extra-allow',
    'clashing-init-and-init-var',
    'model-config-invalid-field-name',
    'with-config-on-model',
    'dataclass-on-model',
    'validate-call-type',
    'unpack-typed-dict',
    'overlapping-unpack-typed-dict',
    'invalid-self-type',
    'validate-by-alias-and-name-false',
]


"""

from __future__ import annotations

__all__ = ("ExitStatus", "CleoErrorMixin", "CleoErrorCodes")

import enum
from typing import Literal, LiteralString





CleoErrorCodes = Literal[
    "validator-argument-default-value",
    "cmd-invalid-option",
    "cmd-invalid-argument",
    "argument-set-default-value",
    "argument-not-list-type",
]


class CleoErrorMixin:
    """
    A mixin class for common functionality shared by all Miloto-specific errors.
    """

    def __init__(self, message: str, *, code: LiteralString | None) -> None:
        """
        :param message: A message describing the error.
        :param code: An optional error code from PydanticErrorCodes enum.
        """
        self.message = message
        self.code = code

    def __str__(self) -> str:
        if self.code is None:
            return self.message
        else:
            return f"{self.message} {self.code}"


class MyExceptionGroup(ExceptionGroup):
    """
    Documentation: https://peps.python.org/pep-0654/#exceptiongroup-and-baseexceptiongroup
                   https://peps.python.org/pep-0654/
    Usage:
    >>> import traceback
    >>> eg = ExceptionGroup(
    >>>     "one",
    >>>     [
    >>>         TypeError(1),
    >>>         ExceptionGroup(
    >>>             "two",
    >>>              [TypeError(2), ValueError(3)]
    >>>         ),
    >>>         ExceptionGroup(
    >>>              "three",
    >>>               [OSError(4)]
    >>>         )
    >>>     ]
    >>> )
    >>> traceback.print_exception(eg)


    >>> eg = MyExceptionGroup("eg", [TypeError(1), ValueError(2)], 42)
    >>> match, rest = eg.split(ValueError)
    >>> print(f'match: {match!r}: {match.errcode}')
    match: MyExceptionGroup('eg', [ValueError(2)], 42): 42
    >>> print(f'rest: {rest!r}: {rest.errcode}')
    rest: MyExceptionGroup('eg', [TypeError(1)], 42): 42
    >>>

    """

    def __new__(cls, message, excs, errcode):
        obj = super().__new__(cls, message, excs)
        obj.errcode = errcode
        return obj

    def derive(self, excs):
        return MyExceptionGroup(self.message, excs, self.errcode)


#
#

#
#

#
#
# class CleoCommandError(Exception):
#     def __init__(self, msg: str, title: str = "", command_name: str = "") -> None:
#         super().__init__(msg)
#         self.msg = msg
#         self.title = title
#         self.command_name = command_name
#
#
# def pretty_print_warning(title: str, message: str) -> None:
#     from rich import print as rich_print
#
#     # Columns(
#     #     [message, ],
#     #     column_first=
#     # )
#
#     rich_print(
#         Panel.fit(
#             message,
#             title=title,
#             title_align="left",
#             border_style="green",
#         )
#     )
