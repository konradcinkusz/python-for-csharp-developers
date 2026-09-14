"""Way out 2: import inside the function, so the import happens at call time.

Cheap after the first call -- it is a dict lookup in sys.modules -- and it
moves the whole question out of import order. The cost is that a reader has
to go and find it, which is why it belongs in the smallest scope that works.
"""

CURRENCY = "GBP "


def describe(amount: float) -> str:
    from ._pricing_fixed import format_total

    return f"Order total: {format_total(amount)}"
