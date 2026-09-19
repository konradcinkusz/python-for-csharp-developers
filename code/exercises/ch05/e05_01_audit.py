"""Exercise 5.1 -- a decorator is middleware, not metadata.

Write `audit` so that it wraps a function, appends one line to CALLS every
time the wrapped function is called, and leaves the function usable exactly
as before -- same result, same __name__, same docstring.

The test checks all four things, and the last two are what functools.wraps
is for. Without it a decorated function reports the wrapper's name, and
every log line, every traceback and every framework that reads __name__
says `wrapper`.
"""

from collections.abc import Callable

CALLS: list[str] = []


def audit[**P, T](fn: Callable[P, T]) -> Callable[P, T]:
    """Return a wrapper that records the call in CALLS and delegates."""
    raise NotImplementedError("your turn: replace this line")
