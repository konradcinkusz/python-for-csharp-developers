"""Shared scaffolding for chapter 10's exercises.

Every exercise here is handed a database that is already seeded, so the
work is the query and never the fixture. The model and the statement
counter are the chapter's own, imported from code/ch10/ rather than copied,
so an exercise cannot quietly be about a different schema from the page.
"""

from __future__ import annotations

from sqlalchemy import Engine

from ch10.counting import Selects
from ch10.model import Base, Incident, Service, seeded_engine

__all__ = ["Base", "Engine", "Incident", "Selects", "Service", "engine"]


def engine() -> Engine:
    """The chapter's five services and nine incidents, in memory."""
    return seeded_engine()
