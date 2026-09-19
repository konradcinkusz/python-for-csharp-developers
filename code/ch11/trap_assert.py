"""Two failing asserts, kept so the chapter can print what pytest says.

Nothing collects this file: the name does not begin with `test_`. Name it
and pytest runs it anyway, which is worth knowing on its own -- the
discovery pattern governs SEARCHING, not an argument you gave explicitly.

    uv run pytest ch11/trap_assert.py

The two failures are chosen for what the report does with them: the first
gets the sub-expression that produced the value, the second gets a diff.
"""

from pricing import Line, line_total


def skus(lines: list[Line]) -> list[str]:
    return [line.sku for line in lines]


def test_a_scalar_gets_its_working_shown() -> None:
    line = Line("SKU-1", qty=3, unit_pence=250)
    assert line_total(line) == 700


def test_a_collection_gets_a_diff() -> None:
    lines = [Line("SKU-1", 2, 500), Line("SKU-2", 1, 1000)]
    assert skus(lines) == ["SKU-1", "SKU-3"]
