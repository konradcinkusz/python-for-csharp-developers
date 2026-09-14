"""Reference solution for exercise 10.1."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ch10.model import Incident, Service


def critical_services(session: Session) -> list[str]:
    """Names of services with a severity-1 incident, sorted."""
    statement = (
        select(Service.name)
        .join(Service.incidents)
        .where(Incident.severity == 1)
        .order_by(Service.name)
        .distinct()
    )
    return list(session.scalars(statement))
