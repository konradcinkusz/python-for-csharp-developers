"""D.4 -- merge overlapping intervals.

sorted() on tuples compares element by element, so no comparer is needed:
that is the row a C# engineer writes an IComparer or an OrderBy lambda
for. Tuples are immutable, so the running interval is replaced rather than
mutated.

Run it from code/:

    uv run python appd/p04_merge_intervals.py
"""

from __future__ import annotations

from collections.abc import Iterable


# --8<-- [start:solution]
def merge_intervals(
    spans: Iterable[tuple[int, int]],
) -> list[tuple[int, int]]:
    """Overlapping or touching spans, merged, in order."""
    merged: list[tuple[int, int]] = []
    for low, high in sorted(spans):
        if merged and low <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], high))
        else:
            merged.append((low, high))
    return merged
# --8<-- [end:solution]


def main() -> int:
    print(merge_intervals([(1, 3), (2, 6), (8, 10), (15, 18)]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
