"""Exercise 4.1 -- value equality that survives a set.

`Seat` should compare by row and number, and it should still be usable as a
dict key and a set member. Those are two requirements, not one: defining
__eq__ is what takes the second away, so an implementation that stops after
__eq__ passes the first test and fails the rest.

The contract, which is the same one C# states for Equals and GetHashCode:

  * two seats with the same row and number are equal;
  * a seat is not equal to a seat with a different row or number;
  * comparing with something that is not a Seat returns NotImplemented, so
    Python can try the other operand's __eq__ before giving up;
  * equal seats hash equal, so a set of two equal seats holds one.

The last one is the contract's whole point. A hash that disagrees with
equality is worse than no hash at all: the object goes into a dict and
cannot be found again.
"""

from __future__ import annotations


class Seat:
    """A seat, compared by value and usable as a dict key."""

    def __init__(self, row: str, number: int) -> None:
        self.row = row
        self.number = number

    def __repr__(self) -> str:
        return f"Seat({self.row!r}, {self.number!r})"

    def __eq__(self, other: object) -> bool:
        raise NotImplementedError("your turn: replace this line")

    # The method that is missing on purpose is __hash__. Writing __eq__
    # above and stopping there is the trap this exercise exists for.
