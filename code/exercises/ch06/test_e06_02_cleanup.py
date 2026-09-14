import pytest

from exercises._loader import load


def test_reads_and_closes() -> None:
    module = load("ch06", "e06_02_cleanup")
    cursor = module.Cursor([1, 2, 3])
    assert module.read_all(cursor) == [1, 2, 3]
    assert cursor.closed


def test_a_failed_read_still_closes() -> None:
    module = load("ch06", "e06_02_cleanup")
    cursor = module.Cursor([1], fail_after=1)
    with pytest.raises(OSError):
        module.read_all(cursor)
    assert cursor.closed, "the cursor was left open by the failing path"


def test_the_failure_is_not_swallowed() -> None:
    module = load("ch06", "e06_02_cleanup")
    cursor = module.Cursor([1], fail_after=1)
    with pytest.raises(OSError, match="connection lost"):
        module.read_all(cursor)
