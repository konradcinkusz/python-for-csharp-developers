"""Exercise 13.3 -- a token is a quantity, and a price is money.

Every reply carries the two counts that decide the bill. A service that
does not add them up finds out what it spent from the invoice.

Write `call_cost` to price one reply. Providers quote a rate per million
tokens, input and output are charged differently, and the answer is money
-- so it is a `Decimal`, for the same reason it is `decimal` and never
`double` in C#, and it is quantised to the nearest hundredth of a penny so
that summing a month of them does not drift.
"""

from __future__ import annotations

from decimal import Decimal

PENCE = Decimal("0.01")


def call_cost(
    input_tokens: int,
    output_tokens: int,
    input_per_million: Decimal,
    output_per_million: Decimal,
) -> Decimal:
    """The cost of one reply in pence, to the nearest hundredth."""
    raise NotImplementedError("your turn: replace this line")
