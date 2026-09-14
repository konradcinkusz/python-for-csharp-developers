"""Reference solution for exercise 9.2."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


class Incident(BaseModel):
    """Given."""

    title: str = Field(min_length=1)
    severity: int = Field(ge=1, le=5)


def build_app() -> FastAPI:
    app = FastAPI()

    @app.exception_handler(RequestValidationError)
    async def problem(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors: dict[str, list[str]] = {}
        for error in exc.errors():
            field = ".".join(str(part) for part in error["loc"][1:])
            errors.setdefault(field, []).append(error["msg"])
        return JSONResponse(
            status_code=400,
            media_type="application/problem+json",
            content={
                "type": "about:blank",
                "title": "One or more validation errors occurred.",
                "status": 400,
                "instance": request.url.path,
                "errors": errors,
            },
        )

    @app.post("/incidents")
    def create(body: Incident) -> Incident:
        return body

    return app
