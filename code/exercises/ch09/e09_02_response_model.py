"""Exercise 9.3 -- the wire name and the field name are different things.

The service stores an incident with three fields. The caller may see two of
them, under camelCase names; the third must not leave the process, and the
model must still be constructible from Python with ordinary snake_case
keyword arguments.

Complete `IncidentView` and `build_app` so that GET /incidents/{id}:

  * answers {"incidentId": ..., "shortTitle": ...} and nothing else;
  * can be built in Python as IncidentView(incident_id=..., short_title=...);
  * declares exactly those two properties in the generated OpenAPI schema.

The hint is that `alias` renames a field in BOTH directions, which is one
direction too many here.
"""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, SecretStr


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
    """What the caller sees. Declare the two fields and their wire names."""


def build_app() -> FastAPI:
    """Return an application with the route described above."""
    raise NotImplementedError("your turn: replace this line")
