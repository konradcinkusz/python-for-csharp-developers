"""The service skeleton: settings, lifespan, a dependency, two routes.

Everything Chapter 9 argues is in this one file, in the order the request
meets it. Run it and it exercises itself through TestClient, which needs no
server and no port:

    uv run python ch09/service.py

To serve it for real, from code/:

    uv run uvicorn ch09.service:app --port 8000
"""

from __future__ import annotations

from collections.abc import AsyncGenerator, Iterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Request
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# --8<-- [start:settings]
class Settings(BaseSettings):
    """IOptions<T>, except that the binding is also the validation."""

    model_config = SettingsConfigDict(
        env_prefix="OPS_", env_file=".env", extra="forbid"
    )

    database_url: str = "sqlite+aiosqlite:///./ops.db"
    request_timeout_seconds: float = Field(default=5.0, gt=0)
# --8<-- [end:settings]


# --8<-- [start:models]
class IncidentIn(BaseModel):
    """The model binder and the validator, in one declaration."""

    title: str = Field(min_length=1, max_length=120)
    severity: int = Field(ge=1, le=5)


class IncidentOut(BaseModel):
    """serialization_alias, not alias: output only.

    A plain `alias` renames the field on the way IN as well, so the model
    can no longer be built by field name -- and the checker says so before
    the test does. JsonPropertyName renames the wire, not the constructor.
    """

    incident_id: str = Field(serialization_alias="incidentId")
    title: str
    severity: int
# --8<-- [end:models]


class Store:
    """Stands in for the database session Chapter 10 replaces it with."""

    def __init__(self, url: str) -> None:
        self.url = url
        self.rows: list[IncidentOut] = []
        self.closed = False

    def add(self, incoming: IncidentIn) -> IncidentOut:
        row = IncidentOut(
            incident_id=f"INC-{len(self.rows) + 1:04d}",
            title=incoming.title,
            severity=incoming.severity,
        )
        self.rows.append(row)
        return row


# --8<-- [start:lifespan]
@asynccontextmanager
async def lifespan(
    app: FastAPI,
) -> AsyncGenerator[dict[str, Settings]]:
    """IHostedService's StartAsync and StopAsync, as one function.

    What it yields becomes request.state, so application-lifetime objects
    are built once here rather than per request.
    """
    settings = Settings()
    yield {"settings": settings}
    # Anything after the yield is StopAsync.


app = FastAPI(title="Ops Copilot", lifespan=lifespan)
# --8<-- [end:lifespan]


# --8<-- [start:depends]
def get_settings(request: Request) -> Settings:
    settings: Settings = request.state.settings
    return settings


def get_store(
    settings: Annotated[Settings, Depends(get_settings)],
) -> Iterator[Store]:
    """A yield dependency is a scope: what follows the yield is Dispose."""
    store = Store(settings.database_url)
    try:
        yield store
    finally:
        store.closed = True


StoreDep = Annotated[Store, Depends(get_store)]
# --8<-- [end:depends]


# --8<-- [start:routes]
@app.post("/incidents", response_model=IncidentOut, status_code=201)
def create_incident(incoming: IncidentIn, store: StoreDep) -> IncidentOut:
    return store.add(incoming)


@app.get("/incidents/{incident_id}", response_model=IncidentOut)
def read_incident(incident_id: str, store: StoreDep) -> IncidentOut:
    for row in store.rows:
        if row.incident_id == incident_id:
            return row
    raise LookupError(incident_id)
# --8<-- [end:routes]


def main() -> int:
    with TestClient(app) as client:
        created = client.post(
            "/incidents", json={"title": "Disk filling up", "severity": 2}
        )
        print("POST  ", created.status_code, created.json())
        rejected = client.post(
            "/incidents", json={"title": "", "severity": 9}
        )
        print("REJECT", rejected.status_code,
              [e["loc"] for e in rejected.json()["detail"]])
        spec = client.get("/openapi.json").json()
        print("SPEC  ", spec["openapi"], sorted(spec["paths"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
