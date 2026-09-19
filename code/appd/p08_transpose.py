"""D.8 -- transpose a matrix.

zip(*matrix) is the whole answer, and `strict=True` is the half worth
writing: without it a ragged matrix silently transposes to the shortest
row rather than raising. C# has no splat, so the C# version indexes.

Run it from code/:

    uv run python appd/p08_transpose.py
"""

from __future__ import annotations

from collections.abc import Sequence


# --8<-- [start:solution]
def transpose(matrix: Sequence[Sequence[int]]) -> list[list[int]]:
    """Rows become columns. Raises on a ragged matrix."""
    return [list(row) for row in zip(*matrix, strict=True)]
# --8<-- [end:solution]


def main() -> int:
    print(transpose([[1, 2, 3], [4, 5, 6]]))
    try:
        transpose([[1, 2], [3]])
    except ValueError as exc:
        print(f"ragged: ValueError: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
