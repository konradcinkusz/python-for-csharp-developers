"""Exercise 7.4 -- write the composition root.

`announce` below needs a clock and somewhere to send its line. It takes
both as arguments, so it names no concrete type and a test can hand it
anything of the right shape.

What is missing is the one function that knows which concrete types exist.
Write build(clock, sink) so that it returns a callable taking just the
name -- functools.partial is the whole of it -- and the test will wire it
with a fake clock and a list, and check that nothing was patched.
"""

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
    raise NotImplementedError("your turn: bind clock and sink to announce")
