"""Reference solution for exercise 5.4."""

import contextlib
from collections.abc import Generator

EVENTS: list[str] = []


@contextlib.contextmanager
def lease(name: str) -> Generator[str]:
    """Acquire on entry, release on exit, whatever the body does."""
    EVENTS.append(f"acquire {name}")
    try:
        yield name
    finally:
        EVENTS.append(f"release {name}")
