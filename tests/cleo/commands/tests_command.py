from __future__ import annotations

from typing import TYPE_CHECKING
from typing import ClassVar

from cleo.application import Application
from cleo.commands.command import Command
from cleo.helpers import argument
from cleo.testers.command_tester import CommandTester
from tests.fixtures.inherited_command import ChildCommand
from tests.fixtures.signature_command import SignatureCommand


if TYPE_CHECKING:
    from cleo.io.inputs.argument import Argument