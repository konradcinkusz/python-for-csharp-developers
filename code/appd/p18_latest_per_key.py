"""D.18 -- the most recent row per key.

The C# answer is GroupBy then a MaxBy inside each group, which builds
every group before discarding all but one of each. One pass with a
dictionary does not, and the difference shows on a large input.

Run it from code/:

    uv run python appd/p18_latest_per_key.py
"""

from __future__ import annotations

from collections.abc import Callable, Iterable


# --8<-- [start:solution]
def latest_per_key[T](
    rows: Iterable[T],
    key: Callable[[T], str],
    when: Callable[[T], int],
) -> list[T]:
    """One row per key -- the one with the largest `when` -- key order."""
    best: dict[str, T] = {}
    for row in rows:
        k = key(row)
        if k not in best or when(row) > when(best[k]):
            best[k] = row
    return [best[k] for k in sorted(best)]
# --8<-- [end:solution]


def main() -> int:
    rows = [
        {"user": "ada", "at": 1},
        {"user": "ada", "at": 5},
        {"user": "bob", "at": 2},
    ]
    for row in latest_per_key(rows, lambda r: str(r["user"]),
                              lambda r: int(r["at"])):
        print(row)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
