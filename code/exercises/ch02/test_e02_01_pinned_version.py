"""Driven by this book's own uv.lock, so it asks a real question.

Nothing here writes down a version. The declared pin is read out of
pyproject.toml and the resolved one out of uv.lock, and the test asserts
they agree -- which is what `uv sync --locked` guarantees and what a
hand-maintained requirements.txt cannot.
"""

import tomllib
from pathlib import Path
from typing import Any

import pytest

from exercises._loader import load

CODE = Path(__file__).resolve().parents[2]


def _lock() -> dict[str, Any]:
    return tomllib.loads((CODE / "uv.lock").read_text(encoding="utf8"))


def _declared(name: str) -> str:
    """The version pyproject.toml pins `name` to, as a person wrote it."""
    pyproject: dict[str, Any] = tomllib.loads(
        (CODE / "pyproject.toml").read_text(encoding="utf8")
    )
    project: dict[str, Any] = pyproject["project"]
    runtime: list[str] = project["dependencies"]
    for requirement in runtime:
        if requirement.lower().startswith(f"{name}=="):
            return requirement.split("==", 1)[1]
    raise AssertionError(f"{name} is not a declared runtime dependency")


def test_agrees_with_what_the_project_declared() -> None:
    module = load("ch02", "e02_01_pinned_version")
    assert module.pinned(_lock(), "pydantic") == _declared("pydantic")


def test_finds_a_package_nobody_declared() -> None:
    # anyio is nobody's declared dependency here; it arrives underneath
    # httpx and fastapi. The lock pins it anyway, and that is the half of
    # a lockfile a requirements.txt written by hand always misses.
    module = load("ch02", "e02_01_pinned_version")
    version = module.pinned(_lock(), "anyio")
    assert version and version[0].isdigit()


def test_is_case_insensitive() -> None:
    module = load("ch02", "e02_01_pinned_version")
    assert module.pinned(_lock(), "SQLAlchemy") == module.pinned(
        _lock(), "sqlalchemy"
    )


def test_raises_for_something_not_in_the_lock() -> None:
    module = load("ch02", "e02_01_pinned_version")
    with pytest.raises(KeyError):
        module.pinned(_lock(), "not-a-real-distribution")
