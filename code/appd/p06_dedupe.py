"""D.6 -- remove duplicates, keeping first-seen order.

dict.fromkeys is the idiom, and it works because a dict has preserved
insertion order since 3.7. A HashSet in C# does not, so the C# answer
needs both a set and a list; here the dict is both.

Run it from code/:

    uv run python appd/p06_dedupe.py
"""

from __future__ import annotations

from collections.abc import Hashable, Iterable


# --8<-- [start:solution]
def dedupe[T: Hashable](items: Iterable[T]) -> list[T]:
    """Items with duplicates dropped, first occurrence kept in place."""
    return list(dict.fromkeys(items))
# --8<-- [end:solution]


def main() -> int:
    print(dedupe([3, 1, 3, 2, 1]))
    print(dedupe("mississippi"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
