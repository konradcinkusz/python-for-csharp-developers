"""Three ways to lose a failure, and which of them your tools catch.

Run it from code/:

    uv run python ch06/swallow.py

Each shape below turns a failure into a plausible answer. Two of the three
are caught by the linter this book pins, and one of those is caught by the
interpreter as well; the third is caught by nothing at all, which is why it
is the one that reaches production.
"""

from __future__ import annotations

import warnings
from typing import Any


class Ledger:
    """Stands in for anything that can be half-written."""

    def __init__(self) -> None:
        self.rows: list[int] = []
        self.closed = False

    def add(self, row: int) -> None:
        if row < 0:
            raise ValueError(f"negative row: {row}")
        self.rows.append(row)


# --8<-- [start:blind]
def total_blind(ledger: Ledger, rows: list[int]) -> int:
    """Catch everything, log nothing, carry on. Nothing flags this."""
    try:
        for row in rows:
            ledger.add(row)
    except Exception:  # a crash becomes a wrong number
        pass
    return sum(ledger.rows)
# --8<-- [end:blind]


# --8<-- [start:narrow]
def total_narrow(ledger: Ledger, rows: list[int]) -> int:
    """Catch the one failure you can answer, and answer it."""
    for row in rows:
        try:
            ledger.add(row)
        except ValueError:
            ledger.add(0)
    return sum(ledger.rows)
# --8<-- [end:narrow]


# The interpreter refuses to compile this quietly, so it cannot be a
# function in this file: `python ch06/swallow.py` would print the warning
# before any of it ran, and every listing in this book runs clean. Compiling
# it here is how the listing shows you the warning instead of causing it.
# --8<-- [start:finally]
RETURN_IN_FINALLY = """
def total(ledger, rows):
    try:
        for row in rows:
            ledger.add(row)
        return sum(ledger.rows)
    finally:
        return -1
"""


def compile_it(source: str) -> tuple[list[str], dict[str, Any]]:
    """Compile a source string and report what the compiler said about it."""
    namespace: dict[str, Any] = {}
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        exec(compile(source, "<listing>", "exec"), namespace)
    said = [f"{w.category.__name__}: {w.message}" for w in caught]
    return said, namespace
# --8<-- [end:finally]


def main() -> None:
    rows = [3, -1, 4]

    print(f"total_blind:  {total_blind(Ledger(), rows)}")
    print(f"total_narrow: {total_narrow(Ledger(), rows)}")

    said, namespace = compile_it(RETURN_IN_FINALLY)
    for line in said:
        print(f"compiler:     {line}")
    swallowing = namespace["total"]
    print(f"and it still: {swallowing(Ledger(), rows)}")


if __name__ == "__main__":
    main()
