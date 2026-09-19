"""Reference solution for exercise 5.5."""

from dataclasses import dataclass
from typing import cast

ACTIVE = "active"


class Status:
    ACTIVE = "active"


@dataclass(frozen=True)
class Retry:
    after: int


@dataclass(frozen=True)
class Fail:
    reason: str


def route(message: object) -> str:
    """Return the routing decision for one message."""
    match message:
        case Retry(after=0):
            return "now"
        case Retry(after=n) if n > 60:
            return "later"
        case Retry(after=n):
            return f"in {n}s"
        case Fail():
            return "dead letter"
        case list():
            # A pattern match against `object` cannot give the elements a
            # type, so pyright's strict mode calls the capture partially
            # unknown. Declaring the parameter as a union fixes it --
            # ch05/matching.py does exactly that -- but the test here
            # deliberately passes values outside any union, so one cast
            # carries it instead.
            return f"batch of {len(cast(list[object], message))}"
        case {"status": Status.ACTIVE}:
            return "keep"
        case _:
            return "drop"
