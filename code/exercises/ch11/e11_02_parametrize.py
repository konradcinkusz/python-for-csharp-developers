"""Exercise 11.2 -- four tests that differ only in their numbers.

Collapse them into ONE test function with `@pytest.mark.parametrize`, so
that the four cases are data rather than four copies of a sentence. Keep all
four cases: the threshold, either side of it, and zero.

The test beside this file requires your version to pass, to contain exactly
one test function, and to use parametrize.
"""

from pricing import DELIVERY_PENCE, FREE_DELIVERY_PENCE, delivery_pence


def test_nothing_ordered_pays_delivery() -> None:
    assert delivery_pence(0) == DELIVERY_PENCE


def test_a_penny_under_the_threshold_pays_delivery() -> None:
    assert delivery_pence(FREE_DELIVERY_PENCE - 1) == DELIVERY_PENCE


def test_exactly_the_threshold_is_free() -> None:
    assert delivery_pence(FREE_DELIVERY_PENCE) == 0


def test_over_the_threshold_is_free() -> None:
    assert delivery_pence(FREE_DELIVERY_PENCE + 1) == 0
