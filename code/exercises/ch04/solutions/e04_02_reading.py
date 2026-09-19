"""Solution to 4.2 -- the flags are the answer.

frozen=True is the immutability and is also what lets @dataclass write
__hash__; order=True writes the four comparison dunders from the field
order; slots=True is free here and is the part C# gets from a struct.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass


@dataclass(frozen=True, order=True, slots=True)
class Reading:
    """A temperature reading. Immutable, hashable, ordered, replaceable."""

    taken_at: str
    celsius: float

    def warmer_by(self, amount: float) -> Reading:
        """Return a new reading, `amount` warmer. Do not mutate self."""
        return dataclasses.replace(self, celsius=self.celsius + amount)
