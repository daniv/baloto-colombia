from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

if TYPE_CHECKING:
    from pathlib import Path


class Locker:
    def __init__(self, lock: Path, pyproject_data: dict[str, Any]) -> None:
        self._lock = lock
        self._pyproject_data = pyproject_data
        self._lock_data: dict[str, Any] | None = None

    @property
    def lock(self) -> Path:
        return self._lock

    @property
    def lock_data(self) -> dict[str, Any]:
        if self._lock_data is None:
            self._lock_data = self._get_lock_data()

        return self._lock_data

    def is_locked(self) -> bool:
        """
        Checks whether the locker has been locked (lockfile found).
        """
        return self._lock.exists()

    def _get_lock_data(self) -> dict[str, Any]:
        import tomllib

        if not self.lock.exists():
            raise RuntimeError("No lockfile found. Unable to read locked packages")

        with self.lock.open("rb") as f:
            try:
                lock_data = tomllib.load(f)
            except tomllib.TOMLDecodeError as e:
                raise RuntimeError(f"Unable to read the lock file ({e}).")

        return lock_data
