"""Way out 3, part two: depends on _money, and on nothing above it."""

from ._money import CURRENCY


def format_total(amount: float) -> str:
    return f"{CURRENCY}{amount:.2f}"
