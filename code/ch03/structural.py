"""A Protocol is satisfied by shape, not by declaration.

Run it from code/:

    uv run python ch03/structural.py

Nothing below implements Closable. Nothing below imports it, mentions it or
knows it exists. Two of the three satisfy it anyway, because a Protocol
asks what a type HAS rather than what it said it was -- which is why one
can be written for a class you do not own, including a class in the
standard library.
"""

import io
from collections.abc import Iterable
from typing import Protocol, runtime_checkable


@runtime_checkable
class Closable(Protocol):
    """What this function needs, written down. An interface, declared by
    the consumer rather than by every implementer."""

    def close(self) -> None: ...


class Connection:
    """Never heard of Closable. Satisfies it."""

    def __init__(self, dsn: str) -> None:
        self.dsn = dsn

    def close(self) -> None:
        print(f"  closed {self.dsn}")


class Detonator:
    """Has a close(), with a parameter. Does NOT satisfy it."""

    def close(self, force: bool) -> None:
        print(f"  closed, force={force}")


def close_all(items: Iterable[Closable]) -> int:
    """Takes anything with a no-argument close(). No base class in sight."""
    count = 0
    for item in items:
        item.close()
        count += 1
    return count


def main() -> None:
    buffer = io.StringIO()

    print("close_all over a class of mine and one from the library:")
    print("  closed:", close_all([Connection("postgres://db/app"), buffer]))

    # isinstance against a runtime_checkable Protocol asks only whether the
    # attributes are PRESENT. It does not look at the signature, so a class
    # the checker rejects passes the run-time check. pyright will not let
    # that line through silently -- the ignore comment below names the rule
    # it raised, and the rule is called "overlaps unsafely" for this reason.
    overlaps = isinstance(
        Detonator(), Closable  # pyright: ignore[reportGeneralTypeIssues]
    )
    print("isinstance says Detonator is Closable:", overlaps)
    print("the checker disagrees, and the checker is the one that is right")


if __name__ == "__main__":
    main()
