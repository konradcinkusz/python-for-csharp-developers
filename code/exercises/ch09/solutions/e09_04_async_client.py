"""Reference solution for exercise 9.5."""

from __future__ import annotations

from typing import Any

import httpx
from fastapi import FastAPI

app = FastAPI()


@app.get("/incidents/{incident_id}")
async def read(incident_id: str) -> dict[str, str]:
    """Given."""
    return {"incidentId": incident_id, "title": "Disk filling up"}


async def fetch_incident(
    application: FastAPI, incident_id: str
) -> dict[str, Any]:
    transport = httpx.ASGITransport(app=application)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://ops"
    ) as client:
        response = await client.get(f"/incidents/{incident_id}")
    response.raise_for_status()
    body: dict[str, Any] = response.json()
    return body
