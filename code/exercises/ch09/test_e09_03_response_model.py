from types import ModuleType

from fastapi.testclient import TestClient

from exercises._loader import load


def module() -> ModuleType:
    return load("ch09", "e09_03_response_model")


def test_the_wire_names_are_camel_case() -> None:
    body = TestClient(module().build_app()).get("/incidents/INC-0001").json()
    assert set(body) == {"incidentId", "shortTitle"}


def test_the_secret_does_not_leave_the_process() -> None:
    response = TestClient(module().build_app()).get("/incidents/INC-0001")
    assert "pager_token" not in response.text
    assert "pd-secret" not in response.text


def test_it_is_built_from_python_by_field_name() -> None:
    view = module().IncidentView(incident_id="INC-9", short_title="t")
    assert view.incident_id == "INC-9"
    assert view.model_dump() == {
        "incident_id": "INC-9",
        "short_title": "t",
    }


def test_the_schema_declares_the_wire_names() -> None:
    client = TestClient(module().build_app())
    schemas = client.get("/openapi.json").json()["components"]["schemas"]
    assert set(schemas["IncidentView"]["properties"]) == {
        "incidentId",
        "shortTitle",
    }
