"""Exercise 11.1 is about the SHAPE of a test file, so the check is too.

Three things, and none of them reaches into pytest's internals: your tests
still pass, a fixture called `basket` exists, and the basket is built in one
place instead of two. Running pytest over your own file is what makes the
first one a fact rather than a hope.
"""

import re

from exercises._loader import load

from ._pytest_runner import run, source

KEY = "e11_01_fixture"


def test_your_tests_still_pass() -> None:
    result = run(load("ch11", KEY))
    assert result.returncode == 0, result.stdout


def test_there_is_a_fixture_called_basket() -> None:
    src = source(load("ch11", KEY))
    assert re.search(r"^@pytest\.fixture", src, re.M), (
        "no @pytest.fixture in the file"
    )
    assert re.search(r"^def basket\(", src, re.M), (
        "the fixture has to be called `basket`, because that is the name "
        "the tests request it by"
    )


def test_the_basket_is_built_in_one_place() -> None:
    built = len(re.findall(r'Line\("SKU-1"', source(load("ch11", KEY))))
    assert built == 1, (
        f"the basket is still built {built} times; that is the "
        f"duplication the fixture is meant to remove"
    )
