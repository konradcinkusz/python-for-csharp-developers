"""Exercise 5.4 -- a context manager that releases whatever happens.

`lease` must behave like `using (var l = pool.Acquire(name))`: append
"acquire <name>" to EVENTS on the way in, yield the name, and append
"release <name>" on the way out -- on the normal path, on the exception
path, and when the caller breaks out early.

Write it with @contextlib.contextmanager. The test that matters is the one
that raises inside the body: a generator-based context manager without a
try/finally looks correct until something throws, and then the release
line never runs.
"""

from collections.abc import Generator

EVENTS: list[str] = []


def lease(name: str) -> Generator[str]:
    """Acquire on entry, release on exit, whatever the body does."""
    raise NotImplementedError("your turn: replace this line")
