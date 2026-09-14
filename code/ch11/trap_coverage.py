"""A test that executes every line of pricing.py and checks almost nothing.

Kept for one measurement: run it under coverage and the report says the
module is fully covered. It is, in the only sense the tool means -- every
line ran. Whether any of them was right is a different question, and no
coverage tool has ever answered it.

    uv run coverage run --source=pricing -m pytest ch11/trap_coverage.py
    uv run coverage report -m
"""

import contextlib

from pricing import (
    FREE_DELIVERY_PENCE,
    Line,
    line_total,
    order_total,
)


def test_it_returns_something() -> None:
    small = [Line("SKU-1", qty=1, unit_pence=500)]
    large = [Line("SKU-2", qty=1, unit_pence=FREE_DELIVERY_PENCE)]

    # Every line of pricing.py runs. Not one of these says what it should
    # have returned, so the module could return any integer and pass.
    assert order_total(small) is not None
    assert order_total(large) is not None
    assert line_total(small[0]) >= 0

    with contextlib.suppress(ValueError):
        line_total(Line("SKU-3", qty=-1, unit_pence=1))
