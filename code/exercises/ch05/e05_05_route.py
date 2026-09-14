"""Exercise 5.5 -- match, and the pattern that is not a comparison.

`route` takes one decoded message and returns a short string saying what
to do with it. Use a match statement, and cover, in this order:

  * Retry(after=0)                 -> "now"
  * Retry with after above 60      -> "later"
  * any other Retry                -> "in <n>s"
  * Fail, whatever the reason      -> "dead letter"
  * a list, empty or not           -> "batch of <n>"
  * a dict carrying status ACTIVE  -> "keep"
  * anything else                  -> "drop"

ACTIVE is a module-level constant. Writing `case ACTIVE:` will not compare
against it -- a bare name in a pattern binds rather than tests, and Python
will refuse to compile it here because it makes the later cases
unreachable. The spelling that compares is the dotted one.
"""

from dataclasses import dataclass

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
    raise NotImplementedError("your turn: replace this line")
