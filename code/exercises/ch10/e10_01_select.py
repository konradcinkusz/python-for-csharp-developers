"""Exercise 10.1 -- compose the query, do not filter in Python.

Return the names of every service that has at least one severity-1
incident, in alphabetical order.

The test checks the answer AND what the answer cost: exactly one SELECT.
Loading every service and filtering in a loop gives the same list and six
statements, which is the habit this chapter is about.
"""

from __future__ import annotations

from sqlalchemy.orm import Session


def critical_services(session: Session) -> list[str]:
    """Names of services with a severity-1 incident, sorted."""
    raise NotImplementedError("your turn: one select(), one SELECT")
