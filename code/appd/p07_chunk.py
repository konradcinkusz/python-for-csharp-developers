"""D.7 -- split a sequence into fixed-size chunks.

A slice past the end is not an error in Python, which is why the last
chunk needs no special case: items[9:12] on a ten-item list is two items
and not an exception. C#'s Skip/Take has the same forgiveness; an index
range does not.

Run it from code/:

    uv run python appd/p07_chunk.py
"""

from __future__ import annotations

from collections.abc import Sequence


# --8<-- [start:solution]
def chunk[T](items: Sequence[T], size: int) -> list[Sequence[T]]:
    """items in pieces of at most `size`, in order."""
    if size < 1:
        raise ValueError(f"size must be positive, not {size}")
    return [items[i:i + size] for i in range(0, len(items), size)]
# --8<-- [end:solution]


def main() -> int:
    print(chunk([1, 2, 3, 4, 5], 2))
    print(chunk("abcdefg", 3))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
