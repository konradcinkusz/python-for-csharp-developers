"""Reference solution for exercise 6.1."""

from __future__ import annotations


class MissingFieldError(KeyError):
    """A row did not carry a field this code needs."""


def field_of(row: dict[str, str], name: str) -> str:
    """Return row[name].

    Raises:
        MissingFieldError: the row has no such field. Its __cause__ is the
            KeyError the lookup raised.
    """
    try:
        return row[name]
    except KeyError as exc:
        raise MissingFieldError(name) from exc
