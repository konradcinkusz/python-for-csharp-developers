"""Exercise 9.1 -- a dependency with a lifetime.

Build a FastAPI application with one route, GET /incidents, whose handler
asks for a `UnitOfWork` TWICE. The unit of work must be:

  * built by a dependency that YIELDS it, so that the code after the yield
    runs when the response has been sent;
  * the SAME instance for both asks within one request;
  * a NEW instance on the next request;
  * closed -- `uow.closed` set to True -- once the request is over.

The route returns {"same": <bool>, "id": <the unit of work's number>}.
"""

from __future__ import annotations

from fastapi import FastAPI


class UnitOfWork:
    """Given. Every instance registers itself so the test can see it."""

    made: list[UnitOfWork] = []

    def __init__(self) -> None:
        UnitOfWork.made.append(self)
        self.number = len(UnitOfWork.made)
        self.closed = False

    def close(self) -> None:
        self.closed = True


def build_app() -> FastAPI:
    """Return the application described above."""
    raise NotImplementedError("your turn: replace this line")
