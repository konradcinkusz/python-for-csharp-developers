"""D.17 -- de-duplicate by a key function.

DistinctBy arrived in .NET 6; Python has never had it and does not need
it, because a function is an ordinary argument. The set holds the keys
and the list holds the order, which is the pairing problem 6 got for free
from dict.

Run it from code/:

    uv run python appd/p17_dedupe_by.py
"""

from __future__ import annotations

from collections.abc import Callable, Hashable, Iterable


# --8<-- [start:solution]
def dedupe_by[T, K: Hashable](
    items: Iterable[T], key: Callable[[T], K]
) -> list[T]:
    """First item for each distinct key, in first-seen order."""
    seen: set[K] = set()
    kept: list[T] = []
    for item in items:
        k = key(item)
        if k not in seen:
            seen.add(k)
            kept.append(item)
    return kept
# --8<-- [end:solution]


def main() -> int:
    rows = [{"id": 1, "v": "a"}, {"id": 1, "v": "b"}, {"id": 2, "v": "c"}]
    print(dedupe_by(rows, lambda r: r["id"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
