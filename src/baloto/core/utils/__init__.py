from pathlib import Path


def create_link_markup(filepath: str, lineno: int) -> str:
    path = Path(filepath)
    filename = path.name
    linkname = f"{filename}_{lineno}"
    return f"[bright_blue][link={path.as_posix()}:{lineno}][bright_blue u]{linkname}[/link][/] <-click[/]"
