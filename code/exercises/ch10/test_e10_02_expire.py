from exercises._loader import load
from exercises.ch10._db import Selects, engine

EXPECTED = ["API", "DB", "WEB", "QUEUE", "AUTH"]


def test_names_are_upper_cased() -> None:
    module = load("ch10", "e10_02_expire")
    assert module.rename_and_list(engine()) == EXPECTED


def test_reading_back_is_free() -> None:
    module = load("ch10", "e10_02_expire")
    bound = engine()
    with Selects(bound) as counted:
        module.rename_and_list(bound)
    assert counted.count == 1, (
        f"{counted.count} SELECTs: commit() expired the objects and "
        f"reading them back reloaded each one"
    )
