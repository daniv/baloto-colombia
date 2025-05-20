from __future__ import annotations

import hashlib
import inspect
import os
import posixpath
import re
import subprocess

from pathlib import Path
from typing import TYPE_CHECKING
from typing import ClassVar
from typing import cast

from baloto.core.cleo import helpers
from baloto.core.cleo._compat import shell_quote
from baloto.core.cleo.commands.command import Command
from core.cleo.commands.completions.templates import TEMPLATES
from core.cleo.exceptions import CleoRuntimeError


if TYPE_CHECKING:
    from core.cleo.io.inputs.argument import Argument
    from core.cleo.io.inputs.option import Option


class CompletionsCommand(Command):
    name = "completions"
    description = "Generate completion scripts for your shell."
