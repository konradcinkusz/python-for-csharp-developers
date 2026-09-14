"""Reference solution for exercise 10.4.

`with session.begin()` is the transaction. It commits at the end of the
block and rolls back if the block raises, which is TransactionScope with
the complete() call implied by not throwing.

The rollback is what makes this an exercise: the two good rows were
already flushed to the database by the lookup that follows them, and it is
the transaction, not the session, that takes them back out.
"""

from __future__ import annotations

from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from ch10.model import Incident, Service

Entry = tuple[str, str, int]


def record_all(bound: Engine, entries: list[Entry]) -> int:
    """Write every entry or none; return how many were written."""
    with Session(bound) as session, session.begin():
        for name, title, minutes in entries:
            service = session.scalars(
                select(Service).where(Service.name == name)
            ).one()
            service.incidents.append(
                Incident(title=title, severity=3, minutes=minutes)
            )
        return len(entries)
