"""Exercise 7.2 -- say what this module exports.

`from module import *` copies every name that does not begin with an
underscore, which here means the two helpers as well as the two functions
anybody outside should call. Worse, it copies `os` and `Decimal`: a name
this module imported becomes a name its importer appears to export.

Give the module an __all__ naming only `net_total` and `format_money`, and
the star import copies those two and nothing else. The test checks both.
"""

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
