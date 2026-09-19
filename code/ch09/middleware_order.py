"""Middleware order, which is not the order ASP.NET Core runs them in.

Register A and then B. In ASP.NET Core, A is the outer one. Here it is not,
and nothing warns you.

    uv run python ch09/middleware_order.py
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient

Next = Callable[[Request], Awaitable[Response]]

trace: list[str] = []
app = FastAPI()


# --8<-- [start:order]
@app.middleware("http")
async def audit(request: Request, call_next: Next) -> Response:
    trace.append("audit in")
    response = await call_next(request)
    trace.append("audit out")
    return response


@app.middleware("http")
async def timing(request: Request, call_next: Next) -> Response:
    trace.append("timing in")
    response = await call_next(request)
    trace.append("timing out")
    return response
# --8<-- [end:order]


@app.get("/ping")
async def ping() -> dict[str, str]:
    trace.append("handler")
    return {"pong": "yes"}


def main() -> int:
    client = TestClient(app)
    client.get("/ping")
    print("registered:", "audit, then timing")
    print("ran       :", " -> ".join(trace))
    # The reason is one line of starlette: add_middleware does
    # self.user_middleware.insert(0, ...), so each registration goes on
    # the FRONT of the stack and the last one registered is outermost.
    print("outermost :", trace[0].split()[0])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
