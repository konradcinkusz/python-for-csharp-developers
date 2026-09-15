"""The fixtures you did not write, and the markers that select tests.

pytest ships fixtures for the three things a test most often needs and that
xUnit makes you arrange yourself: a scratch directory, the log, and stdout.

    uv run pytest ch11/test_builtins.py -m "not slow"
    uv run python ch11/test_builtins.py
"""

import logging
from pathlib import Path

import pytest
from pricing import Line, order_total


# --8<-- [start:tmp_path]
def test_tmp_path_is_a_real_empty_directory(tmp_path: Path) -> None:
    """A per-test directory, created for you and removed for you.

    It is a `pathlib.Path`, it is empty, and it is unique to this test -- so
    two tests writing `orders.csv` do not collide, and neither has to know
    the other exists.
    """
    report = tmp_path / "orders.csv"
    report.write_text("SKU-1,750\n", encoding="utf8")
    assert report.read_text(encoding="utf8").startswith("SKU-1")
    assert list(tmp_path.iterdir()) == [report]
# --8<-- [end:tmp_path]


# --8<-- [start:caplog]
def test_caplog_captures_records_not_strings(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """`caplog` gives you the LogRecord objects, so assert on fields.

    Asserting on the formatted line couples the test to the formatter, which
    is the thing most likely to change and the thing least worth testing.
    """
    with caplog.at_level(logging.WARNING):
        logging.getLogger("orders").warning("late delivery for %s", "SKU-1")

    assert caplog.records[0].levelname == "WARNING"
    assert caplog.records[0].getMessage() == "late delivery for SKU-1"
# --8<-- [end:caplog]


# --8<-- [start:capsys]
def test_capsys_reads_back_what_was_printed(
    capsys: pytest.CaptureFixture[str],
) -> None:
    print(order_total([Line("SKU-1", qty=1, unit_pence=500)]))
    assert capsys.readouterr().out == "999\n"
# --8<-- [end:capsys]


# --8<-- [start:markers]
@pytest.mark.slow
def test_something_expensive_enough_to_deselect() -> None:
    """`-m "not slow"` deselects this. `[Trait]` plus a filter, in one word.

    A marker must be registered in pyproject.toml or pytest warns: an
    unregistered marker is nearly always a typo, and a typo'd marker is a
    test that quietly never runs under the filter that was meant to select
    it.
    """
    assert order_total([Line("SKU-1", qty=100, unit_pence=100)]) == 10000
# --8<-- [end:markers]


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, *("-q", "--no-header")]))
