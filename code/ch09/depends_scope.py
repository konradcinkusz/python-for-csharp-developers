"""Dependency lifetimes: per request, per use, and per application.

`Depends` is the container, and the three lifetimes a .NET engineer reaches
for are all here -- but the default is not the one the habit expects.

    uv run python ch09/depends_scope.py
"""

from __future__ import annotations

from collections.abc import AsyncGenerator, Iterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Request
from fastapi.testclient import TestClient

trace: list[str] = []
built = {"count": 0}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[dict[str, str]]:
    # Singleton: built once for the process, reached as request.state.
    trace.append("lifespan:open")
    yield {"pool": "the one connection pool"}
    trace.append("lifespan:close")


app = FastAPI(lifespan=lifespan)


# --8<-- [start:scoped]
def connection() -> Iterator[str]:
    """Scoped, and disposable: what follows the yield is the Dispose."""
    built["count"] += 1
    trace.append("open")
    try:
        yield f"connection-{built['count']}"
    finally:
        trace.append("close")


Conn = Annotated[str, Depends(connection)]
Fresh = Annotated[str, Depends(connection, use_cache=False)]
# --8<-- [end:scoped]


# --8<-- [start:route]
@app.get("/twice")
def twice(a: Conn, b: Conn) -> dict[str, str]:
    """Two asks, one request: the SAME instance. Scoped, not transient."""
    trace.append("handler")
    return {"a": a, "b": b}


@app.get("/fresh")
def fresh(a: Conn, b: Fresh) -> dict[str, str]:
    """use_cache=False is how you ask for transient."""
    return {"a": a, "b": b}
# --8<-- [end:route]


@app.get("/singleton")
def singleton(request: Request) -> dict[str, str]:
    pool: str = request.state.pool
    return {"pool": pool}


def main() -> int:
    with TestClient(app) as client:
        first = client.get("/twice").json()
        print("one request, two asks :", first["a"], "and", first["b"])
        print("order                 :", " -> ".join(trace))
        trace.clear()
        second = client.get("/twice").json()
        print("next request          :", second["a"])
        both = client.get("/fresh").json()
        print("use_cache=False       :", both["a"], "and", both["b"])
        print("lifespan state        :",
              client.get("/singleton").json()["pool"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
