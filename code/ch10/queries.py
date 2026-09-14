"""A data layer with no repository: functions that take a Session.

There is no class here, no interface, and nothing to register. A query is a
function whose first parameter is the unit of work, which is what a
repository was wrapping all along -- and because the Session is the seam,
a test swaps the engine rather than the layer.

Run it from code/:

    uv run python ch10/queries.py
"""

from __future__ import annotations

from model import Incident, Service, seeded_engine
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

# --8<-- [start:queries]


def worst_services(session: Session, limit: int) -> list[tuple[str, int]]:
    """Aggregate in the database, because that is what it is for."""
    statement = (
        select(Service.name, func.sum(Incident.minutes).label("lost"))
        .join(Service.incidents)
        .group_by(Service.name)
        .order_by(func.sum(Incident.minutes).desc())
        .limit(limit)
    )
    return [(name, int(lost)) for name, lost in session.execute(statement)]


def service_with_incidents(session: Session, name: str) -> Service | None:
    """One aggregate, loaded whole, in two statements and not six."""
    statement = (
        select(Service)
        .where(Service.name == name)
        .options(selectinload(Service.incidents))
    )
    return session.scalars(statement).one_or_none()


def record(session: Session, name: str, title: str, minutes: int) -> None:
    """A write is a write. The caller owns the transaction, not this."""
    service = session.scalars(
        select(Service).where(Service.name == name)
    ).one()
    service.incidents.append(
        Incident(title=title, severity=3, minutes=minutes)
    )


# --8<-- [end:queries]

# --8<-- [start:caller]


def shift_report(session: Session) -> str:
    """The caller owns the transaction, so a batch is one unit of work."""
    with session.begin():
        record(session, "web", "web-cache-miss", 4)
        record(session, "db", "db-replica-lag", 11)
    return ", ".join(
        f"{name} {lost}m" for name, lost in worst_services(session, 3)
    )


# --8<-- [end:caller]


def main() -> int:
    with Session(seeded_engine()) as session:
        print(f"worst: {shift_report(session)}")
        api = service_with_incidents(session, "api")
        assert api is not None
        print(f"api has {len(api.incidents)} incidents")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
