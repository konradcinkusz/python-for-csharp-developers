"""Reference solution for exercise 10.2.

expire_on_commit=False is the switch. Collecting the names into a list
before the commit is the other answer, and is better when the session is
long-lived: it does not ask the session to hold stale objects, it just
stops needing them.
"""

from __future__ import annotations

from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from ch10.model import Service


def rename_and_list(bound: Engine) -> list[str]:
    """Upper-case every service name, commit, return the names."""
    with Session(bound, expire_on_commit=False) as session:
        services = list(session.scalars(select(Service).order_by(Service.id)))
        for service in services:
            service.name = service.name.upper()
        session.commit()
        return [service.name for service in services]
