"""D.14 -- the longest common prefix of a list of strings.

The trick is that only the smallest and largest strings matter: anything
between them shares at least their common prefix. min and max over
strings compare lexicographically in both languages, so this one carries
across unchanged.

Run it from code/:

    uv run python appd/p14_common_prefix.py
"""

from __future__ import annotations

from collections.abc import Sequence


# --8<-- [start:solution]
def longest_common_prefix(words: Sequence[str]) -> str:
    """The longest string every word starts with."""
    if not words:
        return ""
    first, last = min(words), max(words)
    for i, char in enumerate(first):
        if i >= len(last) or last[i] != char:
            return first[:i]
    return first
# --8<-- [end:solution]


def main() -> int:
    print(repr(longest_common_prefix(["flower", "flow", "flight"])))
    print(repr(longest_common_prefix(["dog", "car"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
