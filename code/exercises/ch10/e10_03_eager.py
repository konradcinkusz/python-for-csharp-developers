"""Exercise 10.3 -- this one already works. Make it stop costing six.

Unlike the others, the starter returns the right answer. It is the loop
everybody writes, and the test fails on what it cost rather than on what
it said: six SELECTs for five services, which is one for the services and
one per service afterwards.

Say what you want up front and it is two, whatever the service count.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ch10.model import Service


def totals(session: Session) -> dict[str, int]:
    """Minutes lost per service."""
    return {
        service.name: sum(i.minutes for i in service.incidents)
        for service in session.scalars(select(Service))
    }
