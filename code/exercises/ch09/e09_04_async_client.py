"""Exercise 9.5 -- exercise the application without starting a server.

`TestClient` is synchronous: it drives the app from a worker thread, which
is fine until the thing under test is itself async and you want it on the
same loop. `httpx.ASGITransport` puts an AsyncClient straight on top of the
application object -- no port, no server, no waiting for readiness.

Complete `fetch_incident` so that it calls GET /incidents/{incident_id} on
the application it is GIVEN, over ASGITransport, and returns the decoded
JSON body. It must not open a socket, and it must close the client it
opened.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI

app = FastAPI()


@app.get("/incidents/{incident_id}")
async def read(incident_id: str) -> dict[str, str]:
    """Given."""
    return {"incidentId": incident_id, "title": "Disk filling up"}


async def fetch_incident(
    application: FastAPI, incident_id: str
) -> dict[str, Any]:
    """Call the application directly and return the decoded body."""
    raise NotImplementedError("your turn: replace this line")
