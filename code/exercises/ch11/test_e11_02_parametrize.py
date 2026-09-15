"""Exercise 11.2: one test function, four cases, and they still pass."""

import re

from exercises._loader import load

from ._pytest_runner import run, source

KEY = "e11_02_parametrize"


def test_your_tests_still_pass() -> None:
    result = run(load("ch11", KEY))
    assert result.returncode == 0, result.stdout


def test_there_is_exactly_one_test_function() -> None:
    functions = re.findall(r"^def (test_\w+)", source(load("ch11", KEY)), re.M)
    assert len(functions) == 1, (
        f"found {len(functions)} test functions ({', '.join(functions)}); "
        f"the point of parametrize is that four cases need one"
    )


def test_the_four_cases_are_data() -> None:
    src = source(load("ch11", KEY))
    assert "parametrize" in src, "no @pytest.mark.parametrize in the file"
    result = run(load("ch11", KEY))
    assert "4 passed" in result.stdout, (
        f"four cases go in, four tests come out; pytest said:\n"
        f"{result.stdout}"
    )
