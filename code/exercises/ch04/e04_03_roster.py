"""Exercise 4.3 -- be a collection without declaring that you are one.

`Roster` wraps a list of names. Give it the methods that make the built-in
syntax work, none of which is declared anywhere:

  * len(roster)          -- how many names
  * roster[2]            -- the name at that index
  * for name in roster   -- iterate in order
  * "ada" in roster      -- membership, CASE-INSENSITIVELY, which is the
                            one that is not just delegation
  * roster.first         -- a read-only computed property, the first name,
                            or None when the roster is empty

The last two are the point. __contains__ is optional -- Python will fall
back to walking __iter__ -- so a roster without it still answers `in`, and
answers it case-sensitively, which is not what this one promises. And
`first` is a property rather than a method, so it is read with no
parentheses and cannot be assigned to.
"""

from __future__ import annotations

from collections.abc import Iterator


class Roster:
    """A list of names that behaves like a collection."""

    def __init__(self, names: list[str]) -> None:
        self._names = names

    def __len__(self) -> int:
        raise NotImplementedError("your turn: replace this line")

    def __getitem__(self, index: int) -> str:
        raise NotImplementedError("your turn: replace this line")

    def __iter__(self) -> Iterator[str]:
        raise NotImplementedError("your turn: replace this line")

    def __contains__(self, value: object) -> bool:
        raise NotImplementedError("your turn: replace this line")

    # `first` is missing entirely, and it is a property rather than a
    # method: the test reads it with no parentheses.
