"""D.12 -- a running total.

itertools.accumulate is the standard library's scan. C# has no Aggregate
that yields the intermediate values, so the C# version keeps a local and
yields it, which is the loop this line replaces.

Run it from code/:

    uv run python appd/p12_running_total.py
"""

from __future__ import annotations

import itertools
from collections.abc import Iterable


# --8<-- [start:solution]
def running_total(amounts: Iterable[int]) -> list[int]:
    """Each element plus everything before it."""
    return list(itertools.accumulate(amounts))
# --8<-- [end:solution]


def main() -> int:
    print(running_total([1, 2, 3, 4]))
    print(running_total([]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
