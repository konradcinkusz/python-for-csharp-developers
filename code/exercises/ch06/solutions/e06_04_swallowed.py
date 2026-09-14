"""Reference solution for exercise 6.4."""

from __future__ import annotations


class BadRowError(ValueError):
    """A row could not be read as an integer."""


def total(rows: list[str]) -> int:
    """Sum `rows`, each of which should be an integer in text.

    Raises:
        BadRowError: a row was not an integer. Its __cause__ is the
            ValueError that int() raised.
    """
    running = 0
    for row in rows:
        try:
            running += int(row)
        except ValueError as exc:
            # The one failure this function can name, named -- rather than
            # every failure, unnamed, turned into a plausible zero.
            raise BadRowError(f"not an integer: {row!r}") from exc
    return running
