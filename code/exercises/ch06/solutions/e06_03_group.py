"""Reference solution for exercise 6.3."""

from __future__ import annotations

from collections.abc import Callable

Check = Callable[[dict[str, str]], None]


def check_all(record: dict[str, str], checks: list[Check]) -> None:
    """Run every check over `record`.

    Raises:
        ExceptionGroup: at least one check raised. The group holds every
            failure, in the order the checks were given.
    """
    failures: list[Exception] = []
    for check in checks:
        try:
            check(record)
        except Exception as exc:
            # Collecting is not swallowing: every one of these is raised
            # again below, together, and none is discarded.
            failures.append(exc)
    if failures:
        raise ExceptionGroup(f"{len(failures)} check(s) failed", failures)
