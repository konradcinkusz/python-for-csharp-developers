"""Solution to 4.1 -- __eq__ and __hash__ written over one key tuple.

Hashing the same tuple __eq__ compares is the cheapest way to keep the two
in step, and it is what @dataclass generates. Writing it by hand once is
worth doing because it shows there is no magic in the generated version.
"""

from __future__ import annotations


class Seat:
    """A seat, compared by value and usable as a dict key."""

    def __init__(self, row: str, number: int) -> None:
        self.row = row
        self.number = number

    def __repr__(self) -> str:
        return f"Seat({self.row!r}, {self.number!r})"

    def _key(self) -> tuple[str, int]:
        return (self.row, self.number)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Seat):
            return NotImplemented
        return self._key() == other._key()

    def __hash__(self) -> int:
        return hash(self._key())
