"""What PyPI, and a user, need from the table.

Six checks. Five are what an upload or an install turns on; the sixth --
that the package declares no runtime dependencies -- is what this package
in particular is entitled to say, because every import in it is stdlib.
"""

import re
import tomllib

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
