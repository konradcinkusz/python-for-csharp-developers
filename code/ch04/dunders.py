"""Every operator is a method, and the protocol is duck-typed.

There is no IComparable to implement and no operator keyword to write. A
class that defines __lt__ sorts; a class that defines __len__ answers len();
a class that defines neither is simply not asked. Nothing declares that it
participates, which is why you can read any library's class and name the C#
feature it is imitating without opening a base class list.

Run it from code/:

    uv run python ch04/dunders.py
"""

from __future__ import annotations

import operator
import re
from collections.abc import Callable
from typing import Any

# --8<-- [start:protocol]
# The operator module is the mapping, written down by the standard library
# rather than by this book: every infix operator is a function, and every
# one of those functions is spelled as a method on the left operand.
OPERATORS: list[tuple[str, Callable[[Any, Any], Any], str]] = [
    ("a + b", operator.add, "__add__"),
    ("a < b", operator.lt, "__lt__"),
    ("a == b", operator.eq, "__eq__"),
    ("a[b]", operator.getitem, "__getitem__"),
]


def supports(value: object, method: str) -> bool:
    """Does this object take part in the protocol that method names?

    This is the whole of the type test Python does. There is no interface
    to be registered against: the method is either there or it is not.
    """
    return hasattr(type(value), method)


def by_operator_and_by_method(a: int, b: int) -> list[str]:
    """The operator and the dunder are the same call, checked rather than
    asserted: each row runs the operator function and the method it names
    and reports that the two agree.
    """
    rows: list[str] = []
    for text, fn, method in OPERATORS:
        if not supports(a, method):
            continue
        agrees = fn(a, b) == getattr(a, method)(b)
        rows.append(f"{text:8}  is  {method:14}  agrees: {agrees}")
    return rows
# --8<-- [end:protocol]


# --8<-- [start:repr]
class Port:
    """__repr__ is the one you owe; __str__ is the one you may not need.

    __repr__ is what the REPL, the debugger and -- the half that catches
    people -- a *list* of these objects shows. __str__ is only what print
    and format show, and it falls back to __repr__ when it is absent. So a
    class with only __str__ defined prints well alone and prints as
    <ch04.dunders.Port object at 0x...> the moment it is inside anything.
    """

    def __init__(self, host: str, number: int) -> None:
        self.host = host
        self.number = number

    def __repr__(self) -> str:
        return f"Port(host={self.host!r}, number={self.number!r})"

    def __str__(self) -> str:
        return f"{self.host}:{self.number}"
# --8<-- [end:repr]


class Bare:
    """The same class with only __str__, to show what a list of them says."""

    def __str__(self) -> str:
        return "bare"


def main() -> int:
    for row in by_operator_and_by_method(7, 2):
        print(row)
    print(f"{'a[b]':8}  is  {'__getitem__':14}  int has it: "
          f"{supports(1, '__getitem__')}")

    port = Port("db.internal", 5432)
    print()
    print(f"str(port)      {port}")
    print(f"repr(port)     {port!r}")
    print(f"a list of them {[port]}")

    # A list of Bare shows its default repr, which carries the object's
    # address -- so the address is replaced here rather than printed, for
    # the same reason the book commits no timing: it differs on every run.
    bare = repr([Bare()])
    print()
    print(f"str(bare)      {Bare()}")
    print(f"a list of them {re.sub(r'0x[0-9a-f]+', '0x...', bare)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
