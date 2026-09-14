"""Reference solution for exercise 13.1."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, ValidationError


class Reply(BaseModel):
    # One line, and E8 measures what it costs: nothing.
    model_config = ConfigDict(strict=True)

    summary: str
    severity: int
    needs_human: bool


def parse_reply(raw: str) -> Reply | None:
    """Parse `raw`, or return None if any field is not the declared type."""
    try:
        return Reply.model_validate_json(raw)
    except ValidationError:
        return None
