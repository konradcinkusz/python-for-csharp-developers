"""Reference solution for exercise 13.3."""

from __future__ import annotations

from decimal import Decimal

PENCE = Decimal("0.01")
MILLION = Decimal(1_000_000)


def call_cost(
    input_tokens: int,
    output_tokens: int,
    input_per_million: Decimal,
    output_per_million: Decimal,
) -> Decimal:
    """The cost of one reply in pence, to the nearest hundredth."""
    total = (
        Decimal(input_tokens) * input_per_million
        + Decimal(output_tokens) * output_per_million
    ) / MILLION
    # quantize, not round(): the exponent is the contract, so a sum of
    # these has a fixed number of places rather than a drifting one.
    return total.quantize(PENCE / Decimal(100))
