"""Exercise 6.2 -- close it on both paths, and let the failure out.

`read_all` must return every row a cursor yields, and it must close the
cursor whether or not reading raised. It must NOT turn a read failure into
a value: the caller is entitled to the exception, and the test checks that
it still arrives.

`using` in C# does both halves for you. Here you write one of them, and the
obvious first draft -- read, then close -- passes the happy-path test and
leaks the handle on every other path.
"""

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
    raise NotImplementedError("your turn: replace this line")
