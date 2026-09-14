"""Half of a cycle that does not survive. Needs a NAME from _orders."""

from ._orders import CURRENCY


def format_total(amount: float) -> str:
    return f"{CURRENCY}{amount:.2f}"
