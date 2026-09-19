"""Exercise 4.2 -- a frozen dataclass is the record, and `replace` is `with`.

Declare `Reading` as a dataclass so that all four hold at once:

  * it is immutable -- assigning to a field raises FrozenInstanceError;
  * it compares by value and is hashable;
  * it orders by `taken_at` first, then `celsius`, so sorted() works with
    no key function;
  * `warmer_by` returns a NEW reading, raised by the given amount, leaving
    the original untouched. Use dataclasses.replace rather than building
    the type by hand: it is `with` on a C# record, and it runs __init__,
    so a field you add later is carried without this method changing.

The decorator arguments are most of the answer, and the order of the two
fields is the rest: @dataclass writes the comparison methods from the field
order as declared, the way a tuple compares.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Reading:
    """A temperature reading. Immutable, hashable, ordered, replaceable."""

    taken_at: str
    celsius: float

    def warmer_by(self, amount: float) -> Reading:
        """Return a new reading, `amount` warmer. Do not mutate self."""
        raise NotImplementedError("your turn: replace this line")
