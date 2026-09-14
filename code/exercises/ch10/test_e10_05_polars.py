import polars as pl
from sqlalchemy import select
from sqlalchemy.orm import Session

from exercises._loader import load
from exercises.ch10._db import Incident, Service, engine

EXPECTED = [("db", 58), ("api", 54), ("auth", 31), ("queue", 25)]


def frame() -> pl.LazyFrame:
    """The same rows the chapter's database holds, as columns."""
    with Session(engine()) as session:
        rows = session.execute(
            select(Service.name, Incident.severity, Incident.minutes)
            .join(Service.incidents)
        ).all()
    return pl.LazyFrame(
        {
            "service": [str(r[0]) for r in rows],
            "severity": [int(r[1]) for r in rows],
            "minutes": [int(r[2]) for r in rows],
        }
    )


def test_returns_a_plan_and_not_rows() -> None:
    module = load("ch10", "e10_05_polars")
    assert isinstance(module.lost_minutes(frame()), pl.LazyFrame)


def test_rows_are_right_once_collected() -> None:
    module = load("ch10", "e10_05_polars")
    plan = module.lost_minutes(frame())
    rows = [(str(s), int(m)) for s, m in plan.collect().rows()]
    assert rows == EXPECTED
