"""Exercise 5.2 -- the closure that captured the variable.

`broken` is written the way a .NET engineer writes it before C# 5, and it
is wrong for the same reason it was wrong then: the three functions share
one variable rather than each holding a copy.

Leave `broken` alone -- a test asserts it stays broken, because the point
is that this compiles and runs. Write `fixed_by_default` and
`fixed_by_partial` so each returned function reports its own index, one
using a default argument and one using functools.partial.
"""

from collections.abc import Callable


def broken(n: int) -> list[Callable[[], int]]:
    """Three closures over one variable. Do not change this.

    ruff's B023 refuses this line; the noqa is what lets the trap exist.
    """
    return [lambda: i for i in range(n)]  # noqa: B023


def fixed_by_default(n: int) -> list[Callable[[], int]]:
    """Same list, each function holding its own index, via a default."""
    raise NotImplementedError("your turn: replace this line")


def fixed_by_partial(n: int) -> list[Callable[[], int]]:
    """Same list again, via functools.partial."""
    raise NotImplementedError("your turn: replace this line")
