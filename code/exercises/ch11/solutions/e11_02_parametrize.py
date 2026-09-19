"""Reference solution for exercise 11.2."""

import pytest
from pricing import DELIVERY_PENCE, FREE_DELIVERY_PENCE, delivery_pence


@pytest.mark.parametrize(
    ("goods", "expected"),
    [
        (0, DELIVERY_PENCE),
        (FREE_DELIVERY_PENCE - 1, DELIVERY_PENCE),
        (FREE_DELIVERY_PENCE, 0),
        (FREE_DELIVERY_PENCE + 1, 0),
    ],
)
def test_delivery_is_free_at_the_threshold_and_above(
    goods: int, expected: int
) -> None:
    assert delivery_pence(goods) == expected
