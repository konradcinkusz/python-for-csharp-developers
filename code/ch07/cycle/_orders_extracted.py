"""Way out 3, part three: one direction only, so there is no cycle left."""

from ._pricing_extracted import format_total


def describe(amount: float) -> str:
    return f"Order total: {format_total(amount)}"
