"""A composition root, with no container, in about thirty lines.

    cd code && uv run python ch07/composition.py

Nothing below imports anything concrete except build(). That is the whole
of the pattern: one function knows which implementations exist, and every
other function is handed what it needs. The test beside this chapter's
exercises substitutes a fake by passing one in -- no registration, no
inheritance, and nothing patched.
"""

from __future__ import annotations

import functools
import sys
from collections.abc import Callable
from datetime import date
from typing import Protocol


# --8<-- [start:ports]
class Clock(Protocol):
    """What the service needs from a clock, and nothing else."""

    def today(self) -> date: ...


class Sink(Protocol):
    """What the service needs from wherever its output goes."""

    def send(self, message: str) -> None: ...
# --8<-- [end:ports]


# --8<-- [start:service]
def check(
    clock: Clock, sink: Sink, name: str, expires_on: date
) -> None:
    """The work. Its collaborators arrive as arguments, like any other."""
    remaining = (expires_on - clock.today()).days
    state = "expired" if remaining < 0 else f"{remaining} days left"
    sink.send(f"{name}: {state}")
# --8<-- [end:service]


# --8<-- [start:adapters]
class SystemClock:
    """The real one. It satisfies Clock by shape; it never says so."""

    def today(self) -> date:
        return date.today()


class StdoutSink:
    def send(self, message: str) -> None:
        print(f"  {message}")
# --8<-- [end:adapters]


# --8<-- [start:root]
def build() -> Callable[[str, date], None]:
    """The composition root: the only function here that names a class.

    functools.partial binds the collaborators and leaves the rest of the
    signature alone, so what comes back is the service with its wiring
    already done -- which is what a container hands you, built by hand.
    """
    clock: Clock = SystemClock()
    sink: Sink = StdoutSink()
    return functools.partial(check, clock, sink)
# --8<-- [end:root]


def main() -> int:
    service = build()
    # A date in the past, so the line below says the same thing whenever
    # this listing is run and the transcript in the book stays true.
    print("wired by build():")
    service("certificate", date(2000, 1, 1))
    # build() is annotated as returning a plain callable, so nothing here
    # can reach past it to ask what it really is -- which is the point, and
    # which pyright enforces.
    print(f"and it is a callable, not a class: {callable(service)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
