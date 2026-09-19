"""D.13 -- rotate a list left by n.

The modulo is the whole problem: rotating by more than the length, or by
a negative amount, has to mean something. Python's % returns the sign of
the divisor, so `by %= len(items)` normalises a negative rotation into a
positive one for free -- in C# it does not, and the C# version needs a
correction.

Run it from code/:

    uv run python appd/p13_rotate.py
"""

from __future__ import annotations

from collections.abc import Sequence


# --8<-- [start:solution]
def rotate[T](items: Sequence[T], by: int) -> list[T]:
    """items rotated left by `by`, which may exceed len or be negative."""
    if not items:
        return list(items)
    by %= len(items)
    return list(items[by:]) + list(items[:by])
# --8<-- [end:solution]


def main() -> int:
    print(rotate([1, 2, 3, 4, 5], 2))
    print(rotate([1, 2, 3, 4, 5], -1))
    print(rotate([1, 2, 3, 4, 5], 7))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
