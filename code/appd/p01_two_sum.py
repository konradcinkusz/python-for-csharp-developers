"""D.1 -- two sum: the dictionary is the index.

The C# answer is the same algorithm with a Dictionary. What differs is
that `target - n in seen` is one lookup rather than TryGetValue's
out-parameter dance, and that the tuple comes back without a type to
declare.

Run it from code/:

    uv run python appd/p01_two_sum.py
"""

from __future__ import annotations

from collections.abc import Sequence


# --8<-- [start:solution]
def two_sum(nums: Sequence[int], target: int) -> tuple[int, int] | None:
    """Indices of the first pair summing to target, or None."""
    seen: dict[int, int] = {}
    for i, n in enumerate(nums):
        if target - n in seen:
            return (seen[target - n], i)
        seen[n] = i
    return None
# --8<-- [end:solution]


def main() -> int:
    print(two_sum([2, 7, 11, 15], 9))
    print(two_sum([1, 2], 99))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
