"""The unit of work, and the four moments a DbContext habit meets it.

A Session is a DbContext: it tracks the objects you put in it, works out
what changed, and writes it in one transaction. What differs is when each
of those happens, and that is what this file prints.

Run it from code/:

    uv run python ch10/session.py
"""

from __future__ import annotations

from counting import Selects
from model import Incident, Service, seeded_engine
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

# --8<-- [start:identity]


def identity_map(session: Session, engine: Engine) -> tuple[bool, int]:
    """Two loads of one row give one object, and the second is free."""
    first = session.get(Service, 1)
    with Selects(engine) as counted:
        second = session.get(Service, 1)
    return first is second, counted.count


# --8<-- [end:identity]

# --8<-- [start:flush]


def flush_then_rollback(session: Session) -> tuple[int | None, int | None]:
    """flush() writes and assigns the key; commit() ends the transaction."""
    service = Service(name="cache")
    session.add(service)
    before = service.id            # None: nothing has been written yet
    session.flush()                # INSERT runs, inside the transaction
    after = service.id             # the database chose it
    session.rollback()             # and the row is gone again
    return before, after


# --8<-- [end:flush]

# --8<-- [start:query]


def slow_services(session: Session, over: int) -> list[str]:
    """select() is LINQ to Entities: composed here, executed at scalars()."""
    statement = (
        select(Service.name)
        .join(Service.incidents)
        .where(Incident.minutes > over)
        .order_by(Service.name)
        .distinct()
    )
    return list(session.scalars(statement))


# --8<-- [end:query]


def main() -> int:
    engine = seeded_engine()
    with Session(engine) as session:
        same, cost = identity_map(session, engine)
        print(f"same object: {same}, second get cost: {cost} SELECT")
        before, after = flush_then_rollback(session)
        print(f"id before flush: {before}, after flush: {after}")
        print(f"slow services: {', '.join(slow_services(session, 10))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
