"""Reference solution for exercise 6.2."""

from __future__ import annotations


class Cursor:
    """Stands in for anything that holds a handle and can fail mid-read."""

    def __init__(self, rows: list[int], fail_after: int | None = None) -> None:
        self._rows = rows
        self._fail_after = fail_after
        self.closed = False

    def read(self) -> list[int]:
        if self._fail_after is not None:
            raise OSError(f"connection lost after {self._fail_after} rows")
        return list(self._rows)

    def close(self) -> None:
        self.closed = True


def read_all(cursor: Cursor) -> list[int]:
    """Return every row, and close the cursor on the way out either way.

    Raises:
        OSError: the read failed. The cursor is closed all the same.
    """
    try:
        return cursor.read()
    finally:
        # No `except`, so nothing is caught and nothing is swallowed: this
        # clause runs on the way past, and the exception carries on.
        cursor.close()
