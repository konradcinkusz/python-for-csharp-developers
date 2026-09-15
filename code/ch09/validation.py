"""The 422, and how to make it look like ProblemDetails.

FastAPI answers a bad body with 422 and pydantic's own error list, not with
400 and RFC 9457. Both shapes are printed here, because the second is a
decision and the first is what you get by default.

    uv run python ch09/validation.py
"""

from __future__ import annotations

import json

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

app = FastAPI()
strict = FastAPI()


class Incident(BaseModel):
    title: str = Field(min_length=1)
    severity: int = Field(ge=1, le=5)


@app.post("/incidents")
def create(body: Incident) -> Incident:
    return body


@strict.post("/incidents")
def create_strict(body: Incident) -> Incident:
    return body


# --8<-- [start:problem]
@strict.exception_handler(RequestValidationError)
async def as_problem_details(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """One handler turns every 422 in the service into RFC 9457."""
    return JSONResponse(
        status_code=400,
        media_type="application/problem+json",
        content={
            "type": "about:blank",
            "title": "One or more validation errors occurred.",
            "status": 400,
            "instance": request.url.path,
            "errors": {
                ".".join(str(p) for p in error["loc"][1:]): [error["msg"]]
                for error in exc.errors()
            },
        },
    )
# --8<-- [end:problem]


def main() -> int:
    bad = {"title": "", "severity": 9}
    default = TestClient(app).post("/incidents", json=bad)
    print(f"default {default.status_code} "
          f"{default.headers['content-type']}")
    for error in default.json()["detail"]:
        where = ".".join(str(p) for p in error["loc"])
        print(f"  {error['type']:18} {where:15} {error['msg']}")
    mapped = TestClient(strict).post("/incidents", json=bad)
    print(f"mapped  {mapped.status_code} {mapped.headers['content-type']}")
    print(json.dumps(mapped.json(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
