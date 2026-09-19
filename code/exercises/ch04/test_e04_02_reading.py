import dataclasses

import pytest

from exercises._loader import load


def _reading_class() -> type:
    return load("ch04", "e04_02_reading").Reading


def test_assigning_to_a_field_is_refused() -> None:
    reading = _reading_class()
    one = reading("09:00", 12.0)
    with pytest.raises(dataclasses.FrozenInstanceError):
        one.celsius = 13.0


def test_it_compares_by_value_and_is_hashable() -> None:
    reading = _reading_class()
    assert reading("09:00", 12.0) == reading("09:00", 12.0)
    assert len({reading("09:00", 12.0), reading("09:00", 12.0)}) == 1


def test_it_sorts_by_time_then_temperature_with_no_key() -> None:
    reading = _reading_class()
    unsorted = [
        reading("10:00", 9.0),
        reading("09:00", 15.0),
        reading("09:00", 12.0),
    ]
    assert [r.celsius for r in sorted(unsorted)] == [12.0, 15.0, 9.0]


def test_warmer_by_returns_a_new_reading_and_leaves_the_old_one() -> None:
    reading = _reading_class()
    original = reading("09:00", 12.0)
    raised = original.warmer_by(2.5)
    assert raised == reading("09:00", 14.5)
    assert original.celsius == 12.0
    assert raised is not original
