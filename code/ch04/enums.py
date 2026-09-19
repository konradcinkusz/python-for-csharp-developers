"""Enum, StrEnum and Flag against a C# enum, and the one that is not a Flag.

A C# enum is a named integer, and it is an integer everywhere: it compares
to one, it serialises as one, and an undeclared value is still assignable.
Python's Enum is a class whose members are singletons, so the member is NOT
the integer -- which is the difference that costs a serialisation bug
before it buys anything.

Run it from code/:

    uv run python ch04/enums.py
"""

from __future__ import annotations

import json
from enum import Enum, Flag, StrEnum, auto


# --8<-- [start:kinds]
class Severity(Enum):
    """A plain Enum member is not its value. `Severity.LOW == 1` is False."""

    LOW = 1
    HIGH = 2


class Region(StrEnum):
    """StrEnum members ARE strings, so json.dumps needs nothing from you."""

    EU = "eu"
    US = "us"


class Permission(Flag):
    """Flag is [Flags]: members combine with |, and `in` tests membership.

    auto() on a Flag hands out powers of two, which is the part everyone
    writes by hand in C# and gets wrong once.
    """

    READ = auto()
    WRITE = auto()
    ADMIN = auto()
# --8<-- [end:kinds]


# --8<-- [start:serialise]
def serialise() -> tuple[str, str]:
    """The difference that bites, in one line each.

    A StrEnum member is a str, so it serialises as itself. A plain Enum
    member is not its value, so json.dumps refuses it and you must reach
    for `.value` -- which is exactly the line people forget, because in C#
    the enum went out as a number without being asked.
    """
    region = json.dumps({"region": Region.EU})
    severity = json.dumps({"severity": Severity.HIGH.value})
    return region, severity
# --8<-- [end:serialise]


def main() -> int:
    print(f"Severity.LOW          {Severity.LOW}")
    # pyright refuses this comparison statically -- "no overlap" -- which
    # is the C# habit caught at author time rather than in production.
    # The line is kept, and suppressed, because the chapter's point is
    # that it compiles and returns False.
    same = Severity.LOW == 1  # pyright: ignore[reportUnnecessaryComparison]
    print(f"  == 1                {same}")
    print(f"  .value == 1         {Severity.LOW.value == 1}")
    print(f"  is Severity.LOW     {Severity(1) is Severity.LOW}")

    print()
    print(f"Region.EU             {Region.EU!r}")
    # Also flagged, and also correct: a StrEnum member IS a str, so the
    # check is redundant. Printing it is how the reader sees that.
    is_str = isinstance(  # pyright: ignore[reportUnnecessaryIsInstance]
        Region.EU, str
    )
    print(f"  is a str            {is_str}")
    print(f"  == 'eu'             {Region.EU == 'eu'}")

    both = Permission.READ | Permission.WRITE
    print()
    print(f"READ | WRITE          {both}")
    print(f"  READ in it          {Permission.READ in both}")
    print(f"  ADMIN in it         {Permission.ADMIN in both}")
    print(f"  auto() values       {[p.value for p in Permission]}")

    region, severity = serialise()
    print()
    print(f"json StrEnum          {region}")
    print(f"json Enum needs value {severity}")
    try:
        json.dumps({"severity": Severity.HIGH})
    except TypeError as exc:
        print("json Enum without it  TypeError:")
        print(f"  {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
