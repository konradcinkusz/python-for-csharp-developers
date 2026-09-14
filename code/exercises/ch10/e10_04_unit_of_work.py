"""Exercise 10.4 -- one batch, one transaction.

Record several incidents in one go. Every entry names a service; an entry
naming a service that does not exist is a mistake, and the whole batch has
to fail rather than half of it landing.

Raise the exception. Leave the database as it was.
"""

from __future__ import annotations

from sqlalchemy import Engine

Entry = tuple[str, str, int]


def record_all(bound: Engine, entries: list[Entry]) -> int:
    """Write every entry or none; return how many were written."""
    raise NotImplementedError("your turn: all of them, or none of them")
