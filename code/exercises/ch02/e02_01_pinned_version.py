"""Exercise 2.1 -- read the lockfile, not the wish list.

A `uv.lock` is TOML. Its `[[package]]` array has one entry per resolved
distribution, each with a `name` and a `version`, and it covers the WHOLE
graph -- including the packages nobody wrote down.

Make `pinned` return the exact version the lock holds a distribution at,
and raise `KeyError` naming the distribution when the lock does not carry
it at all. The test beside this file drives it with this book's own
uv.lock, so it is answering the question for a real environment.
"""

from typing import Any


def pinned(lock: dict[str, Any], name: str) -> str:
    """Return the version `lock` pins `name` to.

    Matching is case-insensitive: a distribution is named `SQLAlchemy` on
    one page and `sqlalchemy` on another and they are the same project.

    Raise KeyError(name) when the lock has no such distribution.
    """
    raise NotImplementedError("your turn: replace this line")
