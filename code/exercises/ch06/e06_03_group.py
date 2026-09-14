"""Exercise 6.3 -- report every failure, not the first one.

`check_all` runs a list of checks over one record. The obvious version
stops at the first failure, so a caller who fixes it has to run the job
again to find the second. Write the version that runs every check and
raises once, with all of them.

This is what AggregateException is for, and `ExceptionGroup` is the Python
spelling. Raise nothing when every check passes.
"""

from __future__ import annotations

from collections.abc import Callable

Check = Callable[[dict[str, str]], None]


def check_all(record: dict[str, str], checks: list[Check]) -> None:
    """Run every check over `record`.

    Raises:
        ExceptionGroup: at least one check raised. The group holds every
            failure, in the order the checks were given.
    """
    raise NotImplementedError("your turn: replace this line")
