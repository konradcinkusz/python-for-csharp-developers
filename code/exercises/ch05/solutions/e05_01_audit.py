"""Reference solution for exercise 5.1."""

import functools
from collections.abc import Callable

CALLS: list[str] = []


def audit[**P, T](fn: Callable[P, T]) -> Callable[P, T]:
    """Return a wrapper that records the call in CALLS and delegates."""

    @functools.wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        CALLS.append(fn.__name__)
        return fn(*args, **kwargs)

    return wrapper
