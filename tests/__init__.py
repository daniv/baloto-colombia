# class Formatter(ABC):
#     @abstractmethod
#     def format(self, msg: str) -> str: ...


# class BuilderLogFormatter(Formatter):
#     def format(self, msg: str) -> str:
#         if msg.startswith("Building "):
#             msg = re.sub("Building (.+)", "  - Building <info>\\1</info>", msg)
#         elif msg.startswith("Built "):
#             msg = re.sub("Built (.+)", "  - Built <success>\\1</success>", msg)
#         elif msg.startswith("Adding: "):
#             msg = re.sub("Adding: (.+)", "  - Adding: <b>\\1</b>", msg)
#         elif msg.startswith("Executing build script: "):
#             msg = re.sub(
#                 "Executing build script: (.+)",
#                 "  - Executing build script: <b>\\1</b>",
#                 msg,
#             )
#
#         return msg


# FORMATTERS = {
#     "poetry.core.masonry.builders.builder": BuilderLogFormatter(),
#     "poetry.core.masonry.builders.sdist": BuilderLogFormatter(),
#     "poetry.core.masonry.builders.wheel": BuilderLogFormatter(),
# }

# POETRY_FILTER = logging.Filter(name="poetry")


# class IOFormatter(logging.Formatter):
#     def format(self, record: logging.LogRecord) -> str:
#         if not record.exc_info:
#             level = record.levelname.lower()
#             msg = record.msg
#             func = record.funcName
#             lineno = record.lineno
#
#             if record.name in FORMATTERS:
#                 msg = FORMATTERS[record.name].format(msg)
#             # elif level in self._colors:
#             else:
#                 msg = f" | {func}.{lineno} | [{level}]{msg}[/]"
#
#             record.msg = msg
#
#         formatted = super().format(record)
#
#         if not POETRY_FILTER.filter(record):
#             # prefix all lines from third-party packages for easier debugging
#             formatted = textwrap.indent(
#                 formatted, f"[dim bold]\\[{_log_prefix(record)}][/]", lambda line: True
#             )
#
#         return formatted


# class ConsoleHandler(logging.Handler):
#     def __init__(self, console: Console, err_console: Console) -> None:
#         self._console = console
#         self._error_console = err_console
#
#         super().__init__()
#
#     def emit(self, record: logging.LogRecord) -> None:
#         try:
#             msg = self.format(record)
#             level = record.levelname.lower()
#             err = level in ("warning", "error", "exception", "critical")
#             if err:
#                 self._error_console.print(msg)
#             else:
#                 self._console.print(msg)
#         except Exception:
#             self.handleError(record)


# def _path_to_package(path: Path) -> str | None:
#     """Return main package name from the LogRecord.pathname."""
#     prefix: Path | None = None
#     # Find the most specific prefix in sys.path.
#     # We have to search the entire sys.path because a subsequent path might be
#     # a sub path of the first match and thereby a better match.
#     for syspath in sys.path:
#         if (prefix and prefix in (p := Path(syspath)).parents and p in path.parents) or (
#             not prefix and (p := Path(syspath)) in path.parents
#         ):
#             prefix = p
#     if not prefix:
#         # this is unexpected, but let's play it safe
#         return None
#     path = path.relative_to(prefix)
#     return path.parts[0]  # main package name

# def _log_prefix(record: logging.LogRecord) -> str:
#     prefix = _path_to_package(Path(record.pathname)) or record.module
#     if record.name != "root":
#         prefix = ":".join([prefix, record.name])
#     return prefix
