"""One test, not two, and that is the mechanism rather than a style.

The starter here already returns the right answer, so a separate
correctness test would PASS on it -- and `make starters` runs every
exercise test under a strict expected-failure marker, which turns a
starter that passes into a build failure. An exercise whose fault is cost
rather than correctness therefore has to ask both questions in one test,
which is also the honest verdict: right answer, wrong number of queries.
"""

from sqlalchemy.orm import Session

from exercises._loader import load
from exercises.ch10._db import Selects, engine

EXPECTED = {"api": 59, "db": 58, "web": 7, "queue": 34, "auth": 31}


def test_right_answer_in_at_most_two_statements() -> None:
    module = load("ch10", "e10_03_eager")
    bound = engine()
    with Session(bound) as session, Selects(bound) as counted:
        totals = module.totals(session)
    assert totals == EXPECTED
    assert counted.count <= 2, (
        f"{counted.count} SELECTs for five services: that is one per "
        f"service, and it grows with the table"
    )
