"""Reference solution for exercise 10.3.

selectinload is Include: a second statement for the children of everything
just loaded, rather than a statement per parent. joinedload also passes
the test at one statement, and pays for it by repeating each parent row
once per child, which is why its result needs unique().
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ch10.model import Service


def totals(session: Session) -> dict[str, int]:
    """Minutes lost per service."""
    statement = select(Service).options(selectinload(Service.incidents))
    return {
        service.name: sum(i.minutes for i in service.incidents)
        for service in session.scalars(statement)
    }
