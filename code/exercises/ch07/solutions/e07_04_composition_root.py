"""Solution 7.4 -- the composition root is a function.

partial binds the two collaborators and leaves the rest of the signature
alone, so what comes back is the service, wired. There is no registration
step, no lifetime to declare and nothing to resolve: the caller that built
it holds it.
"""

import functools
from collections.abc import Callable
from datetime import date
from typing import Protocol


class Clock(Protocol):
    def today(self) -> date: ...


class Sink(Protocol):
    def send(self, message: str) -> None: ...


def announce(clock: Clock, sink: Sink, name: str) -> None:
    """The work. Everything it needs arrives as an argument."""
    sink.send(f"{name} checked on {clock.today().isoformat()}")


def build(clock: Clock, sink: Sink) -> Callable[[str], None]:
    """Return `announce` with its collaborators already bound."""
    return functools.partial(announce, clock, sink)
