import pytest
from sqlalchemy import Engine, func, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from exercises._loader import load
from exercises.ch10._db import Incident, engine

GOOD = [("api", "api-retry-storm", 6), ("db", "db-vacuum", 21)]
MIXED = [("api", "api-retry-storm", 6), ("nope", "does-not-exist", 3)]
SEEDED = 9


def incidents(bound: Engine) -> int:
    with Session(bound) as session:
        return session.scalar(select(func.count()).select_from(Incident)) or 0


def test_a_good_batch_is_written() -> None:
    module = load("ch10", "e10_04_unit_of_work")
    bound = engine()
    assert module.record_all(bound, GOOD) == len(GOOD)
    assert incidents(bound) == SEEDED + len(GOOD)


def test_a_bad_entry_takes_the_whole_batch_with_it() -> None:
    module = load("ch10", "e10_04_unit_of_work")
    bound = engine()
    with pytest.raises(NoResultFound):
        module.record_all(bound, MIXED)
    assert incidents(bound) == SEEDED, "half the batch landed"
