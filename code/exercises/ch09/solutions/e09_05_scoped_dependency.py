"""Reference solution for exercise 9.1."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, FastAPI


class UnitOfWork:
    """Given. Every instance registers itself so the test can see it."""

    made: list[UnitOfWork] = []

    def __init__(self) -> None:
        UnitOfWork.made.append(self)
        self.number = len(UnitOfWork.made)
        self.closed = False

    def close(self) -> None:
        self.closed = True


def get_unit_of_work() -> Iterator[UnitOfWork]:
    unit = UnitOfWork()
    try:
        yield unit
    finally:
        unit.close()


Unit = Annotated[UnitOfWork, Depends(get_unit_of_work)]


def build_app() -> FastAPI:
    app = FastAPI()

    @app.get("/incidents")
    def read(first: Unit, second: Unit) -> dict[str, object]:
        return {"same": first is second, "id": first.number}

    return app
