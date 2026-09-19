"""D.3 -- first non-repeating character.

Counter is a Dictionary<char,int> with the counting written for you, and
`next(..., None)` is FirstOrDefault over a generator expression. Two
passes, and the second one stops at the first hit rather than building a
list nobody wanted.

Run it from code/:

    uv run python appd/p03_first_unique.py
"""

from __future__ import annotations

from collections import Counter


# --8<-- [start:solution]
def first_unique(text: str) -> str | None:
    """The first character that occurs exactly once, or None."""
    counts = Counter(text)
    return next((c for c in text if counts[c] == 1), None)
# --8<-- [end:solution]


def main() -> int:
    print(first_unique("swiss"))
    print(first_unique("aabb"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
