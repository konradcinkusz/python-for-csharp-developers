"""A trivial module, here so that the module beside it can import it.

    cd code && uv run python ch07/shop/discount.py
"""

RATE = 0.10


def apply(amount: float) -> float:
    """Take RATE off `amount`."""
    return round(amount * (1 - RATE), 2)


if __name__ == "__main__":
    print(apply(100.0))
