"""Reference solution for exercise 11.1."""

import pytest
from pricing import Line, goods_total, order_total

DELIVERY_PENCE = 499


@pytest.fixture
def basket() -> list[Line]:
    return [Line("SKU-1", qty=2, unit_pence=500), Line("SKU-2", 1, 1000)]


def test_goods_total_adds_the_lines(basket: list[Line]) -> None:
    assert goods_total(basket) == 2000


def test_a_small_order_pays_delivery(basket: list[Line]) -> None:
    assert order_total(basket) == 2000 + DELIVERY_PENCE
