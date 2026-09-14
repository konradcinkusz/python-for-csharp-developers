"""The other half. Needs a NAME from _pricing, which needs one from here."""

from ._pricing import format_total

CURRENCY = "GBP "


def describe(amount: float) -> str:
    return f"Order total: {format_total(amount)}"
