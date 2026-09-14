"""Reference solution for exercise 3.2."""

from collections.abc import Iterable
from typing import Protocol, runtime_checkable


@runtime_checkable
class Closable(Protocol):
    """What close_all needs, written down by the consumer."""

    def close(self) -> None: ...


def close_all(items: Iterable[object]) -> int:
    """Close everything closable; return how many were closed."""
    closed = 0
    for item in items:
        if isinstance(item, Closable):
            item.close()
            closed += 1
    return closed
