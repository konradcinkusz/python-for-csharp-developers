from types import ModuleType

from fastapi.testclient import TestClient

from exercises._loader import load

BAD = {"title": "", "severity": 9}
GOOD = {"title": "Disk filling up", "severity": 2}


def client() -> TestClient:
    module: ModuleType = load("ch09", "e09_01_problem_details")
    return TestClient(module.build_app())


def test_status_is_400_not_422() -> None:
    assert client().post("/incidents", json=BAD).status_code == 400


def test_content_type_is_problem_json() -> None:
    response = client().post("/incidents", json=BAD)
    assert response.headers["content-type"].startswith(
        "application/problem+json"
    )


def test_errors_are_keyed_by_field_without_the_body_prefix() -> None:
    body = client().post("/incidents", json=BAD).json()
    assert set(body["errors"]) == {"title", "severity"}
    assert isinstance(body["errors"]["title"], list)
    assert body["errors"]["title"]


def test_it_carries_status_and_instance() -> None:
    body = client().post("/incidents", json=BAD).json()
    assert body["status"] == 400
    assert body["instance"] == "/incidents"
    assert body["title"]


def test_a_valid_body_is_still_accepted() -> None:
    response = client().post("/incidents", json=GOOD)
    assert response.status_code == 200
    assert response.json() == GOOD
