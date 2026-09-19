"""match is a switch expression that destructures, with one sharp edge.

A modern C# switch expression gives you type, property and relational
patterns. Python's match has all three plus sequence and mapping
patterns, and one rule that has no C# counterpart: a bare name in a
pattern is a CAPTURE, not a comparison. `case ACTIVE:` does not test
against the constant ACTIVE; it matches anything and rebinds the name.

Run it from code/:

    uv run python ch05/matching.py
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Retry:
    after: int


@dataclass(frozen=True)
class Fail:
    reason: str


class Status:
    ACTIVE = "active"


# A declared union is what a C# switch over a sealed hierarchy has and an
# `object` parameter has not: it is what lets the checker narrow inside
# each case, and what lets it tell you a case is unreachable.
type Message = Retry | Fail | list[str] | dict[str, str] | str | int


# --8<-- [start:match]
def describe(event: Message) -> str:
    """Type, property, sequence, mapping and relational patterns, in turn."""
    match event:
        case Retry(after=0):
            return "retry immediately"
        case Retry(after=n) if n > 60:
            return f"retry in {n}s -- that is a long time"
        case Retry(after=n):
            return f"retry in {n}s"
        case Fail(reason=reason):
            return f"gave up: {reason}"
        case [first, *rest]:
            return f"batch of {len(rest) + 1} starting {first!r}"
        case {"status": Status.ACTIVE}:
            return "a dotted name IS compared, unlike a bare one"
        case str() as text:
            return f"plain text: {text!r}"
        case _:
            return "no idea"
# --8<-- [end:match]


# --8<-- [start:capture]
def looks_like_a_constant(value: str) -> str:
    """The trap: ACTIVE here is a capture pattern, so this matches ANY str.

    Python refuses this outright when a case follows it -- the compiler
    says the remaining patterns are unreachable. It compiles in silence
    only when it is the LAST case, which is where it survives review.
    """
    match value:
        case ACTIVE:  # noqa: F841, N806  -- binds, never compares
            return f"matched, and ACTIVE is now {ACTIVE!r}"
# --8<-- [end:capture]


def main() -> int:
    for event in (
        Retry(0), Retry(30), Retry(120), Fail("no quota"),
        ["a", "b", "c"], {"status": "active"}, "hello", 7,
    ):
        print(f"{event!r:26} -> {describe(event)}")
    print(looks_like_a_constant("not active at all"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
