"""Exercise 6.1 -- ask forgiveness, and say who is asking.

`field_of` reads one named field out of a row that came from somewhere
else. Write it in the EAFP shape: act, and turn the one failure you expect
into this module's own error, with the original attached as its cause.

The test checks the cause, so `raise ... from` is not decoration here.
"""

from __future__ import annotations


class MissingFieldError(KeyError):
    """A row did not carry a field this code needs."""


def field_of(row: dict[str, str], name: str) -> str:
    """Return row[name].

    Raises:
        MissingFieldError: the row has no such field. Its __cause__ is the
            KeyError the lookup raised.
    """
    raise NotImplementedError("your turn: replace this line")
