"""Exercise 6.4 -- the one your tools will not catch for you.

`total` sums a batch of rows that arrived as text. The draft this replaces
wrapped the whole sum in `try` / `except Exception` and answered zero, so a
bad batch was indistinguishable from an empty one -- and no linter, checker
or compiler in this book's toolchain said a word about it.

Write the version that sums a good batch, answers zero for an empty one,
and raises `BadRowError` naming the offending row, with the `ValueError`
that int() raised as its cause.
"""

from __future__ import annotations


class BadRowError(ValueError):
    """A row could not be read as an integer."""


def total(rows: list[str]) -> int:
    """Sum `rows`, each of which should be an integer in text.

    Raises:
        BadRowError: a row was not an integer. Its __cause__ is the
            ValueError that int() raised.
    """
    raise NotImplementedError("your turn: replace this line")
