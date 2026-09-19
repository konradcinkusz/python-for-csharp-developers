"""The same cycle as cycle/_pricing.py, flat, beside the script that runs.

Underscored because it is meant to fail on import; ch07/cycles.py imports it
and catches what comes out, so it is exercised on every build.
"""

from _flat_orders import CURRENCY


def format_total(amount: float) -> str:
    return f"{CURRENCY}{amount:.2f}"
