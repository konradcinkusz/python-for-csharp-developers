"""Defining __eq__ sets __hash__ to None. That is the chapter's headline.

In C# the compiler warns you: override Equals and not GetHashCode and you
get CS0659, a warning you have read a hundred times and possibly ignored a
hundred times, because the type still works. Python does not warn. It acts:
the class it hands back has __hash__ set to None, and the object is no
longer hashable at all. The failure is loud, it is at the first dict or set
that touches the object, and it is a long way from the line that caused it.

Run it from code/:

    uv run python ch04/equality.py
"""

from __future__ import annotations


# --8<-- [start:broken]
class NodeBroken:
    """Value equality, and nothing else. This class cannot be a dict key.

    Nothing here mentions hashing. Defining __eq__ is what removed it:
    Python sets __hash__ to None on any class that defines __eq__ and does
    not define __hash__, because an object whose equality you have
    redefined can no longer honour the inherited identity hash.
    """

    def __init__(self, name: str) -> None:
        self.name = name

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, NodeBroken):
            return NotImplemented
        return self.name == other.name
# --8<-- [end:broken]


# --8<-- [start:fixed]
class Node:
    """The same class, hashable, and the two methods agree.

    The contract is C#'s and is not negotiable in either language: equal
    objects must hash equal. Hashing the same tuple that __eq__ compares is
    how you get that for free, and it is what @dataclass writes for you.
    """

    def __init__(self, name: str) -> None:
        self.name = name

    def _key(self) -> tuple[str]:
        return (self.name,)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Node):
            return NotImplemented
        return self._key() == other._key()

    def __hash__(self) -> int:
        return hash(self._key())

    def __repr__(self) -> str:
        return f"Node({self.name!r})"
# --8<-- [end:fixed]


# --8<-- [start:identity]
def identity_report() -> list[str]:
    """`is` asks whether two names are the same object. Never more.

    The folklore says `is` works on small integers and breaks one
    magnitude up. Measured on the pinned interpreter, that is true in a
    REPL and FALSE in a script, and the difference is not the cache the
    folklore names:

      * CPython caches the integers -5 to 256, so a 256 built at run time
        really is the same object as a literal 256;
      * but two literal 257s in ONE code object are also the same object,
        because the compiler stores equal constants in co_consts once. Try
        the classic demonstration inside a function and it does not
        reproduce -- `a = 257; b = 257; a is b` is True.

    So the bug hides from the test you would write for it and appears only
    once a value crosses a run-time boundary, which is where every real
    value comes from: a parsed request, a database row, a JSON payload.
    int(str(n)) below is that boundary, in one call.
    """
    # Two literal occurrences each, in THIS code object. Both pairs come
    # back True, and only the second one surprises anybody.
    small_a, small_b = 256, 256
    big_a, big_b = 257, 257
    literals = {256: small_a is small_b, 257: big_a is big_b}

    lines: list[str] = []
    for n, same_literal in literals.items():
        parsed = int(str(n))  # the run-time boundary, in one call
        lines.append(
            f"{n:5}   two literals: {same_literal!s:5}   "
            f"parsed at run time: {parsed is n!s:5}   "
            f"but == says: {parsed == n}"
        )
    return lines
# --8<-- [end:identity]


def main() -> int:
    print(f"NodeBroken.__hash__ is {NodeBroken.__hash__}")
    try:
        # Both suppressions below are the checker being RIGHT, and they
        # are the chapter's point rather than an escape: pyright refuses
        # this line statically -- "Dictionary key must be hashable" --
        # so the trap CPython only raises on at run time is one the
        # checker Chapter 3 pinned catches while you are still typing.
        # The line is kept so the reader sees the run-time half too.
        {  # pyright: ignore[reportUnusedExpression]
            NodeBroken("db"): 1  # pyright: ignore[reportUnhashable]
        }
    except TypeError as exc:
        # Split at the parenthesis: 3.14's message is 85 characters and a
        # transcript is held to 79, the same budget as a listing.
        head, _, tail = str(exc).partition(" (")
        print(f"as a dict key:      TypeError: {head}")
        print(f"                    ({tail}")

    print()
    print(f"Node.__hash__ is    {Node.__hash__.__qualname__}")
    print(f"as a dict key:      {  {Node('db'): 1}  }")
    print(f"equal objects hash equal: {hash(Node('db')) == hash(Node('db'))}")
    print(f"a set of two equals:      {len({Node('db'), Node('db')})}")

    print()
    for line in identity_report():
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
