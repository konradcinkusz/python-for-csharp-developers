"""Reference solution for exercise 5.3."""

import functools
from collections.abc import Callable


def broken(n: int) -> list[Callable[[], int]]:
    """Three closures over one variable. Do not change this.

    ruff's B023 refuses this line; the noqa is what lets the trap exist.
    """
    return [lambda: i for i in range(n)]  # noqa: B023


def fixed_by_default(n: int) -> list[Callable[[], int]]:
    """Same list, each function holding its own index, via a default."""
    handlers: list[Callable[[], int]] = []
    for i in range(n):
        def handler(bound: int = i) -> int:
            return bound
        handlers.append(handler)
    return handlers


def identity(value: int) -> int:
    return value


def fixed_by_partial(n: int) -> list[Callable[[], int]]:
    """Same list again, via functools.partial."""
    return [functools.partial(identity, i) for i in range(n)]
