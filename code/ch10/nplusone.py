"""The N+1, and the two ways out of it. This is experiment E6.

A relationship is lazy in SQLAlchemy exactly as a navigation property is
lazy in EF Core, so the same loop costs the same shape of query: one for
the parents, then one more per parent. `selectinload` is `Include`, and
`joinedload` is `Include` with a join instead of a second round trip.

Run it from code/:

    uv run python ch10/nplusone.py
"""

from __future__ import annotations

from counting import Selects
from model import Service, seeded_engine
from sqlalchemy import Engine, select
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import Session, joinedload, raiseload, selectinload

# --8<-- [start:lazy]


def total_minutes_lazy(session: Session) -> dict[str, int]:
    """The obvious loop. One SELECT for the services, then one each."""
    return {
        service.name: sum(i.minutes for i in service.incidents)
        for service in session.scalars(select(Service))
    }


# --8<-- [end:lazy]

# --8<-- [start:eager]


def total_minutes_eager(session: Session) -> dict[str, int]:
    """selectinload is Include: a second SELECT, not a second per row."""
    statement = select(Service).options(selectinload(Service.incidents))
    return {
        service.name: sum(i.minutes for i in service.incidents)
        for service in session.scalars(statement)
    }


def total_minutes_joined(session: Session) -> dict[str, int]:
    """joinedload is one statement, and duplicates the parent per child,
    which is why the result needs unique()."""
    statement = select(Service).options(joinedload(Service.incidents))
    return {
        service.name: sum(i.minutes for i in service.incidents)
        for service in session.scalars(statement).unique()
    }


# --8<-- [end:eager]

# --8<-- [start:raiseload]


def refuses_to_lazy_load(session: Session) -> str:
    """raiseload turns the silent N+1 into a failing test."""
    statement = select(Service).options(raiseload(Service.incidents))
    service = session.scalars(statement).first()
    assert service is not None
    try:
        len(service.incidents)
    except InvalidRequestError as exc:
        return str(exc).split(";")[0]
    return "loaded anyway"


# --8<-- [end:raiseload]


def counted(engine: Engine, which: str) -> tuple[int, int]:
    """(SELECTs, services) for one loading strategy."""
    strategies = {
        "lazy": total_minutes_lazy,
        "selectin": total_minutes_eager,
        "joined": total_minutes_joined,
    }
    with Session(engine) as session, Selects(engine) as count:
        totals = strategies[which](session)
    return count.count, len(totals)


def main() -> int:
    engine = seeded_engine()
    for which in ("lazy", "selectin", "joined"):
        selects, services = counted(engine, which)
        print(f"{which:9} {selects} SELECT(s) for {services} services")
    with Session(engine) as session:
        print(f"raiseload: {refuses_to_lazy_load(session)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
