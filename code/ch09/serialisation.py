"""What goes out: response models, aliases, and the generated OpenAPI.

Three things a .NET engineer expects to configure and does not:
serialisation is the response model, the wire name is a field argument, and
the spec is generated from the signatures rather than from XML comments.

    uv run python ch09/serialisation.py
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field, SecretStr

app = FastAPI(title="Ops Copilot")


# --8<-- [start:models]
class IncidentRow(BaseModel):
    """What the service knows. The token never leaves this process."""

    incident_id: str = Field(serialization_alias="incidentId")
    title: str
    pager_token: SecretStr


class IncidentView(BaseModel):
    """What the caller is allowed to see. response_model is the filter."""

    incident_id: str = Field(serialization_alias="incidentId")
    title: str
# --8<-- [end:models]


# --8<-- [start:route]
@app.get("/incidents/{incident_id}", response_model=IncidentView)
def read(incident_id: str) -> IncidentRow:
    # The return annotation is the wider model and the response_model is
    # the narrower one. FastAPI serialises through response_model, so the
    # extra field cannot escape by being returned.
    return IncidentRow(
        incident_id=incident_id,
        title="Disk filling up",
        pager_token=SecretStr("pd-0000"),
    )
# --8<-- [end:route]


def main() -> int:
    client = TestClient(app)
    row = IncidentRow(
        incident_id="INC-1", title="t", pager_token=SecretStr("pd-0000")
    )
    print("model_dump()        ", list(row.model_dump()))
    print("model_dump(by_alias)", list(row.model_dump(by_alias=True)))
    print("on the wire         ", client.get("/incidents/INC-1").json())
    schemas = client.get("/openapi.json").json()["components"]["schemas"]
    for name in sorted(schemas):
        print(f"schema {name:22}", list(schemas[name].get("properties", {})))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
