"""Exercise 10.2 -- read your own objects back after a commit.

Upper-case every service name, commit, and return the names in id order.

The test checks the list AND that the whole function cost one SELECT. The
obvious version costs six: one to load the services and one per service
afterwards, because commit() expired every one of them and reading .name
reloads it.
"""

from __future__ import annotations

from sqlalchemy import Engine


def rename_and_list(bound: Engine) -> list[str]:
    """Upper-case every service name, commit, return the names."""
    raise NotImplementedError("your turn: one SELECT, not one per row")
