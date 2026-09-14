import pytest

from exercises._loader import load


def test_sums_a_good_batch() -> None:
    module = load("ch06", "e06_04_swallowed")
    assert module.total(["1", "2", "39"]) == 42


def test_an_empty_batch_is_zero() -> None:
    module = load("ch06", "e06_04_swallowed")
    assert module.total([]) == 0


def test_a_bad_row_is_not_a_zero() -> None:
    module = load("ch06", "e06_04_swallowed")
    with pytest.raises(module.BadRowError, match="not an integer"):
        module.total(["1", "two", "3"])


def test_the_original_valueerror_is_the_cause() -> None:
    module = load("ch06", "e06_04_swallowed")
    with pytest.raises(module.BadRowError) as caught:
        module.total(["two"])
    assert isinstance(caught.value.__cause__, ValueError)
