"""Solution to 4.3 -- four dunders and one property, nothing declared.

__contains__ is the only one doing more than delegating: without it `in`
falls back to __iter__ and compares exactly, which would make the
case-insensitive promise quietly false.
"""

from __future__ import annotations

from collections.abc import Iterator


class Roster:
    """A list of names that behaves like a collection."""

    def __init__(self, names: list[str]) -> None:
        self._names = names

    def __len__(self) -> int:
        return len(self._names)

    def __getitem__(self, index: int) -> str:
        return self._names[index]

    def __iter__(self) -> Iterator[str]:
        return iter(self._names)

    def __contains__(self, value: object) -> bool:
        if not isinstance(value, str):
            return False
        return value.casefold() in (n.casefold() for n in self._names)

    @property
    def first(self) -> str | None:
        """The first name, or None. Read-only: there is no setter."""
        return self._names[0] if self._names else None
