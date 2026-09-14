from types import ModuleType

from fastapi.testclient import TestClient

from exercises._loader import load


def module() -> ModuleType:
    m = load("ch09", "e09_01_scoped_dependency")
    m.UnitOfWork.made.clear()
    return m


def test_two_asks_in_one_request_share_one_instance() -> None:
    client = TestClient(module().build_app())
    assert client.get("/incidents").json()["same"] is True


def test_one_request_builds_exactly_one() -> None:
    m = module()
    TestClient(m.build_app()).get("/incidents")
    assert len(m.UnitOfWork.made) == 1


def test_the_next_request_gets_a_new_one() -> None:
    m = module()
    client = TestClient(m.build_app())
    first = client.get("/incidents").json()["id"]
    second = client.get("/incidents").json()["id"]
    assert second == first + 1


def test_it_is_closed_when_the_request_is_over() -> None:
    m = module()
    TestClient(m.build_app()).get("/incidents")
    assert all(unit.closed for unit in m.UnitOfWork.made)
