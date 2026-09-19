"""D.9 -- flatten an arbitrarily nested list.

`yield from` is the recursion, and it is what C#'s nested foreach over a
recursive IEnumerable does with more ceremony. The function is a
generator, so nothing is built until somebody walks it.

Run it from code/:

    uv run python appd/p09_flatten.py
"""

from __future__ import annotations

from collections.abc import Iterator

# --8<-- [start:solution]
type Nested = int | list["Nested"]


def flatten(nested: list[Nested]) -> Iterator[int]:
    """Every leaf, left to right, however deeply nested."""
    for item in nested:
        if isinstance(item, list):
            yield from flatten(item)
        else:
            yield item
# --8<-- [end:solution]


def main() -> int:
    print(list(flatten([1, [2, [3, 4]], 5])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
