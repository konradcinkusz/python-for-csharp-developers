"""Way out 1: hold the MODULE, and look the name up when it is needed.

The module object exists from the moment its import begins, so binding it is
always safe. Only reading an attribute off it needs the body to have got
that far -- and by the time anything calls format_total, it has.
"""

from . import _orders_fixed


def format_total(amount: float) -> str:
    return f"{_orders_fixed.CURRENCY}{amount:.2f}"
