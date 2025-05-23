from __future__ import annotations

import sys

from baloto.miloto.application import Application


def main() -> int:
    exit_code: int = Application().run()
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
