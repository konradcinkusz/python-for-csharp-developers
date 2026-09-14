"""Exercise 3.2 -- an interface the implementers never heard of.

Open this file beside the PDF. test_e03_02_protocol.py fails until both
names below do what it expects.

Write `Closable` as a Protocol with one method, `close`, taking no
arguments and returning None, and make it runtime_checkable so that
`isinstance` works against it. Then write `close_all` so that it calls
`close()` on every item that satisfies the protocol, leaves everything
else alone, and returns how many it closed.

Nothing the test passes in will inherit from your protocol. That is the
point of the exercise.
"""

from collections.abc import Iterable
from typing import Protocol, runtime_checkable


@runtime_checkable
class Closable(Protocol):
    """Your turn: one method, and delete this line."""


def close_all(items: Iterable[object]) -> int:
    """Close everything closable; return how many were closed."""
    raise NotImplementedError("your turn: replace this line")
