"""Properties, indexers and IEnumerable, all of them dunder methods.

A C# property is a pair of methods the compiler hides behind a field-like
name. Python's @property is the same trick with the ceremony moved: you
start with a plain attribute and turn it into a property later, without the
callers changing, which is the opposite of C#'s advice to start with a
property because widening a field is a breaking change.

An indexer is __getitem__. IEnumerable is __iter__. Neither is declared.

Run it from code/:

    uv run python ch04/protocols.py
"""

from __future__ import annotations

from collections.abc import Iterator


# --8<-- [start:property]
class Lease:
    """`months` began life as a plain attribute. Nothing outside changed.

    That is the whole argument for not writing a property until you need
    one: in Python the attribute and the property are spelled the same at
    every call site, so promoting one is not a breaking change. In C# a
    field and a property differ in the compiled interface, which is why
    the advice there is to start with a property you do not yet need.
    """

    def __init__(self, months: int) -> None:
        self.months = months

    @property
    def months(self) -> int:
        return self._months

    @months.setter
    def months(self, value: int) -> None:
        if value <= 0:
            raise ValueError(f"a lease runs for at least a month: {value}")
        self._months = value

    @property
    def years(self) -> float:
        """A computed property. No backing field, no setter, read-only."""
        return round(self._months / 12, 2)
# --8<-- [end:property]


# --8<-- [start:container]
class Ledger:
    """__len__, __getitem__, __iter__ and __contains__, none declared.

    Implementing __getitem__ and __len__ is what an indexer plus Count is
    in C#; implementing __iter__ is what IEnumerable<T> is. There is no
    interface on this class and no base to inherit: len(), for, in and [ ]
    each look for their own method and use it if it is there.
    """

    def __init__(self, entries: list[int]) -> None:
        self._entries = entries

    def __len__(self) -> int:
        return len(self._entries)

    def __getitem__(self, index: int) -> int:
        return self._entries[index]

    def __iter__(self) -> Iterator[int]:
        return iter(self._entries)

    def __contains__(self, value: object) -> bool:
        return value in self._entries
# --8<-- [end:container]


def main() -> int:
    lease = Lease(30)
    print(f"months         {lease.months}")
    print(f"years          {lease.years}")
    try:
        lease.months = 0
    except ValueError as exc:
        print(f"setter guard   ValueError: {exc}")

    ledger = Ledger([10, 20, 30])
    print()
    print(f"len()          {len(ledger)}")
    print(f"ledger[1]      {ledger[1]}")
    print(f"for .. in      {[n for n in ledger]}")
    print(f"20 in ledger   {20 in ledger}")
    print(f"sum()          {sum(ledger)}")

    # The duck-typing point, stated as a test rather than as a claim: the
    # class declares no interface, so this is the only thing that decides.
    print()
    for method in ("__len__", "__getitem__", "__iter__", "__contains__"):
        print(f"Ledger has {method:14} {hasattr(Ledger, method)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
