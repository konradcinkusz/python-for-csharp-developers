"""Exercise 11.1 -- turn repeated setup into a fixture.

Two tests below build the same basket, line for line. Replace the
duplication with ONE pytest fixture named `basket`, and have both tests
request it by name.

You will need to import pytest to reach the decorator.

The test beside this file runs pytest over this file and requires three
things: your tests pass, `basket` is a fixture, and neither test builds
its own basket any more.
"""

from pricing import Line, goods_total, order_total

DELIVERY_PENCE = 499


def test_goods_total_adds_the_lines() -> None:
    basket = [Line("SKU-1", qty=2, unit_pence=500), Line("SKU-2", 1, 1000)]
    assert goods_total(basket) == 2000


def test_a_small_order_pays_delivery() -> None:
    basket = [Line("SKU-1", qty=2, unit_pence=500), Line("SKU-2", 1, 1000)]
    assert order_total(basket) == 2000 + DELIVERY_PENCE

