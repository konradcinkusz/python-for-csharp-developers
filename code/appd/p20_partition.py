"""D.20 -- split a sequence in two by a predicate, in one pass.

Two LINQ Wheres walk the input twice and evaluate the predicate twice per
item, which matters when the predicate is expensive or the source is a
generator that can only be walked once. The tuple return is what makes
the one-pass version as convenient as the two-pass one.

Run it from code/:

    uv run python appd/p20_partition.py
"""

from __future__ import annotations

from collections.abc import Callable, Iterable


# --8<-- [start:solution]
def partition[T](
    items: Iterable[T], predicate: Callable[[T], bool]
) -> tuple[list[T], list[T]]:
    """(matching, not matching), in order, in one pass."""
    matching: list[T] = []
    rest: list[T] = []
    for item in items:
        (matching if predicate(item) else rest).append(item)
    return matching, rest
# --8<-- [end:solution]


def main() -> int:
    print(partition([1, 2, 3, 4, 5], lambda n: n % 2 == 0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
