"""Two fixtures on purpose.

A small inline document drives the specifier parsing, because a real
pyproject.toml does not happen to contain every shape a requirement can
take. This book's own file then answers the question the chapter asks: is
the test runner in the set a deployment installs?
"""

import tomllib
from pathlib import Path
from typing import Any

import pytest

from exercises._loader import load

CODE = Path(__file__).resolve().parents[2]

# Every shape a requirement can take, in one table: a bare name, a pin, a
# name with extras and a lower bound, and one carrying an environment
# marker. A real file rarely has all four, which is why this is written
# out rather than read.
SAMPLE: dict[str, Any] = {
    "project": {
        "name": "sample",
        "dependencies": [
            "httpx[http2]>=0.28",
            "pydantic==2.13.5",
            "structlog",
        ],
    },
    "dependency-groups": {
        "dev": ["pytest==9.1.1", "ruff ; python_version >= '3.14'"],
        "docs": ["mkdocs"],
    },
}


def test_runtime_only_by_default() -> None:
    module = load("ch02", "e02_02_install_set")
    assert module.install_set(SAMPLE) == {"httpx", "pydantic", "structlog"}


def test_a_group_adds_to_the_runtime_set() -> None:
    module = load("ch02", "e02_02_install_set")
    assert module.install_set(SAMPLE, ["dev"]) == {
        "httpx",
        "pydantic",
        "structlog",
        "pytest",
        "ruff",
    }


def test_groups_compose() -> None:
    module = load("ch02", "e02_02_install_set")
    both = module.install_set(SAMPLE, ["dev", "docs"])
    assert "mkdocs" in both and "pytest" in both


def test_an_unknown_group_is_an_error_not_an_empty_set() -> None:
    module = load("ch02", "e02_02_install_set")
    with pytest.raises(KeyError):
        module.install_set(SAMPLE, ["dcos"])


def test_this_book_does_not_deploy_its_test_runner() -> None:
    # The question the split exists to answer, asked of the real file.
    module = load("ch02", "e02_02_install_set")
    pyproject: dict[str, Any] = tomllib.loads(
        (CODE / "pyproject.toml").read_text(encoding="utf8")
    )
    runtime = module.install_set(pyproject)
    working = module.install_set(pyproject, ["dev"])
    assert "pydantic" in runtime
    assert "pytest" not in runtime
    assert "pytest" in working
