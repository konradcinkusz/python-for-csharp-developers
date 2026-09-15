"""What PyPI, and a user, need from the table.

Seven checks. Five are what an upload or an install turns on. The sixth
-- that the package declares no runtime dependencies -- is what this
package in particular is entitled to say, because every import in it is
stdlib. The seventh is what makes it usable once installed: the fixture
arrives with the package or the reader is back to editing a conftest.
"""

import re
import tomllib
from typing import cast

from exercises._loader import load

# PEP 503: a distribution name is compared with runs of -, _ and .
# collapsed to a single -, lowercased.
RE_PEP440 = re.compile(r"^\d+(\.\d+)*((a|b|rc)\d+)?(\.post\d+)?(\.dev\d+)?$")


def table() -> dict[str, object]:
    text = load("ch14", "e14_03_publishable").project_table()
    return tomllib.loads(text)["project"]


def normalise(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def test_the_name_is_the_package_not_the_book() -> None:
    assert normalise(str(table()["name"])) == "trace-assert"


def test_the_version_is_a_version() -> None:
    assert RE_PEP440.match(str(table()["version"]))


def test_there_is_a_one_line_summary() -> None:
    description = str(table()["description"])
    assert description.strip()
    assert "\n" not in description
    assert len(description) < 200


def test_it_admits_more_than_one_python_minor() -> None:
    requires = str(table()["requires-python"])
    assert requires.startswith(">=")
    # ">=3.14,<3.15" is the book's own pin and is not a library's.
    assert not re.search(r"<\s*3\.\d+", requires)


def test_it_carries_a_licence_and_a_readme() -> None:
    assert str(table()["license"]).strip()
    assert str(table()["readme"]).strip()


def test_it_declares_no_runtime_dependencies() -> None:
    # Every import in src/trace_assert/ is stdlib. A package that declares
    # what it does not import installs it into everybody's environment.
    assert not table().get("dependencies")


def test_it_registers_the_fixture_as_a_pytest_plugin() -> None:
    # The `trace` fixture reaches a test through one line of conftest.py in
    # chapter 11. A published package does not get to ask for that line:
    # installing it has to be enough, and a pytest11 entry point is how.
    #
    # One cast, at the boundary: `isinstance(x, dict)` narrows to
    # dict[Unknown, Unknown] under strict pyright, so asserting the shape
    # makes the types worse rather than better. Chapter 3 says why.
    points = cast("dict[str, dict[str, str]]", table().get("entry-points", {}))
    assert "trace_assert.plugin" in points.get("pytest11", {}).values()
