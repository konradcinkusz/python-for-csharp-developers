"""Exercise 3.4 -- the rule the chapter ends on, made mechanical.

Validate at the boundary, trust inside. test_e03_04_boundary.py hands
`parse_settings` the kind of JSON a boundary actually delivers -- a port
that is a string, a port that is not a number at all, a document with the
key missing -- and expects a typed object back or a refusal.

Return a Settings with `host` a str and `port` an int, and raise
ValueError for anything you cannot honestly produce that from. Write it by
hand or with pydantic; the test cares about the behaviour and not about
the route, and pydantic's ValidationError is a ValueError.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    host: str
    port: int


def parse_settings(blob: str) -> Settings:
    """Parse JSON into Settings, or raise ValueError."""
    raise NotImplementedError("your turn: replace this line")
