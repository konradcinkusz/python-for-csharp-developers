"""D.19 -- the differences between consecutive readings.

itertools.pairwise, new enough that plenty of Python engineers still
write the index loop. C# has no counterpart in the BCL, so the C# answer
is the index loop -- one of the few rows in this appendix where Python
has the library and C# does not.

Run it from code/:

    uv run python appd/p19_pairwise_diff.py
"""

from __future__ import annotations

import itertools
from collections.abc import Iterable


# --8<-- [start:solution]
def pairwise_diff(readings: Iterable[int]) -> list[int]:
    """Each reading minus the one before it. One shorter than the input."""
    return [b - a for a, b in itertools.pairwise(readings)]
# --8<-- [end:solution]


def main() -> int:
    print(pairwise_diff([10, 13, 12, 20]))
    print(pairwise_diff([7]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
