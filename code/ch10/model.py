"""The model every other listing in this chapter shares.

Two tables: a service, and the incidents raised against it. Declarative
mapping is EF Core's entity class with the fluent configuration moved onto
the attribute: `Mapped[str]` is the column's type AND its NOT NULL, and
`mapped_column()` is where a key, a default or an index goes. There is no
OnModelCreating and no separate configuration class.

Run it from code/:

    uv run python ch10/model.py
"""

from __future__ import annotations

from sqlalchemy import Engine, ForeignKey, create_engine, select
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
)

# --8<-- [start:model]


class Base(DeclarativeBase):
    """One base per database, as one DbContext is per database."""


class Service(Base):
    __tablename__ = "service"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    incidents: Mapped[list[Incident]] = relationship(
        back_populates="service",
    )


class Incident(Base):
    __tablename__ = "incident"

    id: Mapped[int] = mapped_column(primary_key=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("service.id"))
    title: Mapped[str]
    severity: Mapped[int]
    minutes: Mapped[int]
    service: Mapped[Service] = relationship(back_populates="incidents")


# --8<-- [end:model]

# service, title, severity, minutes. Five services, so the N+1 in section
# three costs six statements and the fix costs two: small enough to read,
# far enough apart to be a measurement.
ROWS = (
    ("api", "api-timeouts", 1, 42),
    ("api", "api-5xx-spike", 2, 12),
    ("api", "api-slow-writes", 3, 5),
    ("db", "db-failover", 1, 40),
    ("db", "db-lock-storm", 2, 18),
    ("web", "web-cdn-stale", 3, 7),
    ("queue", "queue-backlog", 2, 25),
    ("queue", "queue-poison-msg", 3, 9),
    ("auth", "auth-token-expiry", 1, 31),
)


def seeded_engine(echo: bool = False) -> Engine:
    """An in-memory SQLite database with the schema and the rows in it."""
    engine = create_engine("sqlite://", echo=echo)
    Base.metadata.create_all(engine)
    services: dict[str, Service] = {}
    with Session(engine) as session:
        for name, title, severity, minutes in ROWS:
            service = services.get(name)
            if service is None:
                service = Service(name=name)
                services[name] = service
                session.add(service)
            service.incidents.append(
                Incident(title=title, severity=severity, minutes=minutes)
            )
        session.commit()
    return engine


def main() -> int:
    engine = seeded_engine()
    with Session(engine) as session:
        names = session.scalars(select(Service.name).order_by(Service.id))
        print(f"services: {', '.join(names)}")
        print(f"incidents: {len(session.scalars(select(Incident)).all())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
