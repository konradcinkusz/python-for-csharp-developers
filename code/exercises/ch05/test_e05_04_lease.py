from types import ModuleType

import pytest

from exercises._loader import load


def _module() -> ModuleType:
    module = load("ch05", "e05_04_lease")
    module.EVENTS.clear()
    return module


def test_the_happy_path_acquires_and_releases() -> None:
    module = _module()
    with module.lease("db") as name:
        module.EVENTS.append(f"using {name}")
    assert module.EVENTS == ["acquire db", "using db", "release db"]


def test_it_releases_when_the_body_raises() -> None:
    module = _module()
    with pytest.raises(ValueError), module.lease("db"):
        raise ValueError("boom")
    assert module.EVENTS == ["acquire db", "release db"]


def test_it_does_not_swallow_the_exception() -> None:
    module = _module()
    with pytest.raises(ValueError, match="boom"), module.lease("db"):
        raise ValueError("boom")


def test_it_nests_and_unwinds_in_reverse() -> None:
    module = _module()
    with module.lease("outer"), module.lease("inner"):
        pass
    assert module.EVENTS == [
        "acquire outer",
        "acquire inner",
        "release inner",
        "release outer",
    ]
