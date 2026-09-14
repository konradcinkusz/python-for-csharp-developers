"""The other half of the flat cycle. See _flat_pricing.py."""

from _flat_pricing import format_total

CURRENCY = "GBP "


def describe(amount: float) -> str:
    return f"Order total: {format_total(amount)}"
