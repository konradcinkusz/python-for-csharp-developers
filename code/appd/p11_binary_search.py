"""D.11 -- binary search, without writing a binary search.

bisect is Array.BinarySearch with a different contract: it returns where
the value WOULD go rather than a negative complement, so the caller checks
whether what is there is what was wanted. That is one comparison instead
of a sign test people get wrong.

Run it from code/:

    uv run python appd/p11_binary_search.py
"""

from __future__ import annotations

import bisect
from collections.abc import Sequence


# --8<-- [start:solution]
def index_of(sorted_items: Sequence[int], value: int) -> int:
    """The index of value in a sorted sequence, or -1."""
    i = bisect.bisect_left(sorted_items, value)
    if i < len(sorted_items) and sorted_items[i] == value:
        return i
    return -1
# --8<-- [end:solution]


def main() -> int:
    print(index_of([1, 3, 5, 7], 5))
    print(index_of([1, 3, 5, 7], 4))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
