"""Solution 7.2 -- the two names the rest of the program may have.

__all__ is the module's public surface, and it is the only thing that
makes `from module import *` mean anything definite. Without it the star
copies every name not starting with an underscore, imported modules
included. With it, the module decides.
"""

__all__ = ["format_money", "net_total"]

import os
from decimal import Decimal

VAT_RATE = Decimal(os.environ.get("PYBOOK_VAT", "0.20"))


def round_pennies(amount: Decimal) -> Decimal:
    """A helper. Correct, useful here, and nobody else's business."""
    return amount.quantize(Decimal("0.01"))


def add_vat(amount: Decimal) -> Decimal:
    """Also a helper."""
    return amount * (1 + VAT_RATE)


def net_total(amounts: list[Decimal]) -> Decimal:
    return round_pennies(add_vat(sum(amounts, Decimal(0))))


def format_money(amount: Decimal) -> str:
    return f"GBP {amount:.2f}"
