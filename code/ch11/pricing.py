"""The module under test for most of this chapter.

Nothing here is interesting. It is deliberately small, deliberately pure and
deliberately has one branch worth arguing about, so that every test in the
chapter is about the TEST and never about the thing being tested.
"""

from dataclasses import dataclass

FREE_DELIVERY_PENCE = 4000
DELIVERY_PENCE = 499


@dataclass(frozen=True, slots=True)
class Line:
    """One line of an order. Money is in pence, and integers, throughout."""

    sku: str
    qty: int
    unit_pence: int


def line_total(line: Line) -> int:
    """What one line costs."""
    if line.qty < 0:
        raise ValueError(f"negative quantity for {line.sku!r}: {line.qty}")
    return line.qty * line.unit_pence


def goods_total(lines: list[Line]) -> int:
    """What the goods cost, before delivery."""
    return sum(line_total(line) for line in lines)


def delivery_pence(goods: int) -> int:
    """Delivery is free at or above the threshold, and charged below it."""
    return 0 if goods >= FREE_DELIVERY_PENCE else DELIVERY_PENCE


def order_total(lines: list[Line]) -> int:
    """Goods plus delivery."""
    goods = goods_total(lines)
    return goods + delivery_pence(goods)
