"""Exercise 9.2 -- give the service the error shape your callers expect.

FastAPI answers an invalid body with 422 and pydantic's own error list.
A .NET caller expects 400 and RFC 9457 problem details. Both are defensible;
what is not defensible is a service where some errors are one shape and some
the other.

Complete `build_app` so that a POST /incidents with an invalid body answers:

  * status 400, not 422;
  * content type application/problem+json;
  * a body carrying "title", "status", "instance" -- the request path -- and
    "errors", a mapping from field name to a LIST of messages, with the
    "body" prefix that pydantic puts in front of every location removed.

A valid body must still be accepted and echoed back unchanged.
"""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field


class Incident(BaseModel):
    """Given."""

    title: str = Field(min_length=1)
    severity: int = Field(ge=1, le=5)


def build_app() -> FastAPI:
    """Return an application that answers invalid bodies as above."""
    raise NotImplementedError("your turn: replace this line")
