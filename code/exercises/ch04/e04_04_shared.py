"""Exercise 4.4 -- the state is shared and nothing at the call site says so.

`Basket` below is broken in the way a C# habit makes most likely: `items`
reads like a field and is a class attribute, so every basket that will ever
exist appends to one list. The first test catches it; the others check that
fixing it did not break anything else.

Fix `Basket` so that:

  * each basket starts empty and keeps its own items;
  * `add` returns the basket, so calls chain;
  * `total` is a computed property, not a method;
  * `Basket.opened` counts how many baskets have been created -- which IS
    shared deliberately, and is what a C# static field actually maps to.

That last one is the half worth being careful about. The bug is not that a
class attribute is shared; it is that a MUTABLE one is shared by accident,
through `self`, with nothing at the call site to say so. A counter
incremented on the class, by name, is the same mechanism used on purpose.
"""

from __future__ import annotations


class Basket:
    """One shopping basket. Every instance currently shares one list."""

    items: list[tuple[str, int]] = []
    opened = 0

    def add(self, name: str, pence: int) -> Basket:
        self.items.append((name, pence))
        return self

    def total(self) -> int:
        return sum(pence for _, pence in self.items)
