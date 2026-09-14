from sqlalchemy.orm import Session

from exercises._loader import load
from exercises.ch10._db import Selects, engine

EXPECTED = ["api", "auth", "db"]


def test_names_are_right() -> None:
    module = load("ch10", "e10_01_select")
    with Session(engine()) as session:
        assert module.critical_services(session) == EXPECTED


def test_costs_one_statement() -> None:
    module = load("ch10", "e10_01_select")
    bound = engine()
    with Session(bound) as session, Selects(bound) as counted:
        module.critical_services(session)
    assert counted.count == 1, (
        f"{counted.count} SELECTs: the database can do the filtering"
    )
