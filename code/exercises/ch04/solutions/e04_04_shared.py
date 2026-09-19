"""Solution to 4.4 -- per-instance state in __init__, the counter on the class.

The mutable list moves into __init__, which is the only place per-instance
state can be created. The counter stays a class attribute and is
incremented through the CLASS name rather than through self: `self.opened
+= 1` would read the class's value, add one, and bind the result as a new
instance attribute, leaving the class's count at zero forever.
"""

from __future__ import annotations


class Basket:
    """One shopping basket, with its own items."""

    opened = 0

    def __init__(self) -> None:
        self.items: list[tuple[str, int]] = []
        Basket.opened += 1

    def add(self, name: str, pence: int) -> Basket:
        self.items.append((name, pence))
        return self

    @property
    def total(self) -> int:
        return sum(pence for _, pence in self.items)
