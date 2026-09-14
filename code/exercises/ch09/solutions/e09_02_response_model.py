"""Reference solution for exercise 9.3."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field, SecretStr


class IncidentRow(BaseModel):
    """Given: what the service holds."""

    incident_id: str
    short_title: str
    pager_token: SecretStr


ROW = IncidentRow(
    incident_id="INC-0001",
    short_title="Disk filling up",
    pager_token=SecretStr("pd-secret"),
)


class IncidentView(BaseModel):
    incident_id: str = Field(serialization_alias="incidentId")
    short_title: str = Field(serialization_alias="shortTitle")


def build_app() -> FastAPI:
    app = FastAPI()

    @app.get("/incidents/{incident_id}", response_model=IncidentView)
    def read(incident_id: str) -> IncidentRow:
        return ROW

    return app
