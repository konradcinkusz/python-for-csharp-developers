"""Exercise 13.1 -- a boundary that does not guess.

`Reply` below is pydantic as it comes, so it coerces: the string "2"
arrives as the integer 2 and nobody is told. At the edge of a service that
is the wrong default -- a provider that starts sending strings has changed
its contract, and you want to hear about it.

Write `parse_reply` so that it accepts a reply whose types are exactly what
`Reply` declares, and returns None for anything else. Do not write the
checks by hand: pydantic has the switch.
"""

from __future__ import annotations

from pydantic import BaseModel


class Reply(BaseModel):
    summary: str
    severity: int
    needs_human: bool


def parse_reply(raw: str) -> Reply | None:
    """Parse `raw`, or return None if any field is not the declared type."""
    raise NotImplementedError("your turn: replace this line")
