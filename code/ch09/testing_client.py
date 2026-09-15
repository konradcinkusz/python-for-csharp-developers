"""Two ways to test a service, and neither needs a port.

TestClient is synchronous and drives the app through a worker thread.
ASGITransport puts httpx's AsyncClient straight on top of the app object,
which is what an async test wants. Both speak to the application, not to a
socket, so there is no server to start and nothing to wait for.

    uv run python ch09/testing_client.py
"""

from __future__ import annotations

import asyncio

import httpx
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()


@app.get("/incidents/{incident_id}")
async def read(incident_id: str) -> dict[str, str]:
    return {"incidentId": incident_id}


# --8<-- [start:sync]
def test_read_sync() -> None:
    """A WebApplicationFactory test, without the factory."""
    client = TestClient(app)
    response = client.get("/incidents/INC-1")
    assert response.status_code == 200
    assert response.json() == {"incidentId": "INC-1"}
# --8<-- [end:sync]


# --8<-- [start:async]
async def test_read_async() -> None:
    """The same test, on the loop the handler actually runs on."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://ops"
    ) as client:
        response = await client.get("/incidents/INC-2")
    assert response.json() == {"incidentId": "INC-2"}
# --8<-- [end:async]


def main() -> int:
    test_read_sync()
    print("TestClient      ok, no port")
    asyncio.run(test_read_async())
    print("ASGITransport   ok, no port")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
