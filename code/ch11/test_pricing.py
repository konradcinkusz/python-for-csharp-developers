"""Discovery, the plain assert, fixtures and parametrize, in one file.

Run it two ways, and it is the same run:

    uv run pytest ch11/test_pricing.py     # as a suite
    uv run python ch11/test_pricing.py     # as a script

The three lines at the bottom are what make the second one work. Every test
listing in this chapter carries them, so a listing is something you can run
rather than something you have to know how to run.
"""

from collections.abc import Iterator

import pytest
from pricing import (
    DELIVERY_PENCE,
    FREE_DELIVERY_PENCE,
    Line,
    delivery_pence,
    goods_total,
    line_total,
    order_total,
)

# Module state, so the teardown below has something to prove it ran.
PRICED: list[int] = []

# --8<-- [start:plain]
# No class, no attribute, no base type. A module whose name starts with
# `test_`, holding functions whose names start with `test_`, IS the suite.


def test_a_line_costs_quantity_times_unit_price() -> None:
    assert line_total(Line("SKU-1", qty=3, unit_pence=250)) == 750
# --8<-- [end:plain]


# --8<-- [start:raises]
def test_a_negative_quantity_is_refused() -> None:
    with pytest.raises(ValueError, match="negative quantity"):
        line_total(Line("SKU-1", qty=-1, unit_pence=250))
# --8<-- [end:raises]


# --8<-- [start:fixture]
@pytest.fixture
def basket() -> list[Line]:
    """Requested by name. A test that wants a basket takes a `basket`."""
    return [Line("SKU-1", qty=2, unit_pence=500), Line("SKU-2", 1, 1000)]


def test_goods_total_adds_the_lines(basket: list[Line]) -> None:
    assert goods_total(basket) == 2000


def test_a_small_order_pays_delivery(basket: list[Line]) -> None:
    assert order_total(basket) == 2000 + DELIVERY_PENCE
# --8<-- [end:fixture]


# --8<-- [start:graph]
@pytest.fixture
def big_basket(basket: list[Line]) -> list[Line]:
    """A fixture may request a fixture. That is the graph, all of it."""
    return [*basket, Line("SKU-3", qty=1, unit_pence=FREE_DELIVERY_PENCE)]


def test_a_large_order_gets_free_delivery(big_basket: list[Line]) -> None:
    assert delivery_pence(goods_total(big_basket)) == 0
# --8<-- [end:graph]


# --8<-- [start:teardown]
@pytest.fixture
def priced_basket(basket: list[Line]) -> Iterator[list[Line]]:
    """Everything before the yield is setup; everything after it is teardown.

    The teardown runs even when the test fails, which is what `using` and
    `IAsyncLifetime.DisposeAsync` buy you -- with no interface to implement
    and no second method to name.
    """
    PRICED.append(goods_total(basket))
    yield basket
    PRICED.clear()


def test_the_fixture_ran_its_setup(priced_basket: list[Line]) -> None:
    assert PRICED == [2000]


def test_and_the_teardown_ran_before_this_one(basket: list[Line]) -> None:
    assert PRICED == []
# --8<-- [end:teardown]


# --8<-- [start:parametrize]
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
# --8<-- [end:parametrize]


# --8<-- [start:runner]
if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, *("-q", "--no-header")]))
# --8<-- [end:runner]
