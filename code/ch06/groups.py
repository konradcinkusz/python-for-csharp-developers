"""More than one failure at a time: ExceptionGroup and except*.

Run it from code/:

    uv run python ch06/groups.py

AggregateException is a container you catch as one exception and then take
apart by hand. An ExceptionGroup is taken apart by the language: `except*`
runs EVERY clause that matches something in the group, and what no clause
matched keeps propagating.
"""

from __future__ import annotations

from collections.abc import Callable

Check = Callable[[dict[str, str]], None]


def has_name(record: dict[str, str]) -> None:
    if not record.get("name"):
        raise ValueError("name is empty")


def has_port(record: dict[str, str]) -> None:
    int(record["port"])  # KeyError when absent, ValueError when not a number


class OwnerMissingError(Exception):
    """A domain error, so that one failure below matches no handler."""


def has_owner(record: dict[str, str]) -> None:
    if "owner" not in record:
        raise OwnerMissingError("no owner")


# --8<-- [start:collect]
def check_all(record: dict[str, str], checks: list[Check]) -> None:
    """Run every check, then raise once with everything that failed.

    Stopping at the first failure would make the caller run the job again
    to find the second one. Raises ExceptionGroup, or nothing.
    """
    failures = [
        exc
        for check in checks
        if (exc := _failure_of(check, record)) is not None
    ]
    if failures:
        raise ExceptionGroup(f"{len(failures)} check(s) failed", failures)


def _failure_of(check: Check, record: dict[str, str]) -> Exception | None:
    try:
        check(record)
    except Exception as exc:  # a check's failure is this function's value
        return exc
    return None
# --8<-- [end:collect]


# --8<-- [start:handle]
def report(record: dict[str, str], checks: list[Check]) -> list[str]:
    """Handle the failures this layer can answer; let the rest go."""
    said: list[str] = []
    try:
        check_all(record, checks)
    except* ValueError as group:
        said += [f"bad value: {e}" for e in group.exceptions]
    except* KeyError as group:
        said += [f"missing key: {e}" for e in group.exceptions]
    return said
# --8<-- [end:handle]


def main() -> None:
    checks = [has_name, has_port, has_owner]

    print("all good:", report({"name": "web", "port": "80", "owner": "ops"},
                              checks))

    try:
        print("two known:", report({"name": ""}, checks[:2]))
    except BaseException as exc:
        print("unexpected:", type(exc).__name__)

    # has_owner raises OwnerMissingError, which no except* clause above
    # matches, so a group with only the unmatched part comes back out.
    try:
        report({"name": ""}, checks)
    except ExceptionGroup as left:
        kinds = [type(e).__name__ for e in left.exceptions]
        print("left uncaught:", kinds, "| message:", left.args[0])


if __name__ == "__main__":
    main()
