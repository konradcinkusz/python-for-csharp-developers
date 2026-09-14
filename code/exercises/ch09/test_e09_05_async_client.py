import socket
from types import ModuleType

import pytest

from exercises._loader import load


def module() -> ModuleType:
    return load("ch09", "e09_05_async_client")


async def test_it_reaches_the_application() -> None:
    m = module()
    body = await m.fetch_incident(m.app, "INC-0001")
    assert body == {
        "incidentId": "INC-0001",
        "title": "Disk filling up",
    }


async def test_it_opens_no_socket(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # If this passes with sockets forbidden, nothing went near the network.
    m = module()

    def refuse(*args: object, **kwargs: object) -> None:
        raise AssertionError("a socket was opened; use ASGITransport")

    monkeypatch.setattr(socket, "socket", refuse)
    monkeypatch.setattr(socket, "create_connection", refuse)
    body = await m.fetch_incident(m.app, "INC-0002")
    assert body["incidentId"] == "INC-0002"


async def test_it_works_against_another_application() -> None:
    # The function takes the application as an argument, so a test can hand
    # it one built for the test rather than the module-level one.
    from fastapi import FastAPI

    other = FastAPI()

    @other.get("/incidents/{incident_id}")
    async def read(incident_id: str) -> dict[str, str]:
        return {"incidentId": incident_id.upper(), "title": "other"}

    body = await module().fetch_incident(other, "inc-3")
    assert body == {"incidentId": "INC-3", "title": "other"}
