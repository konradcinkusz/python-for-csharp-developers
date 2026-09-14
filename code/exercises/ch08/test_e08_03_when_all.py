import pytest

from exercises._loader import load


async def test_results_come_back_in_the_order_asked_for() -> None:
    module = load("ch08", "e08_03_when_all")
    module.cancelled.clear()
    got = await module.fetch_all(["quick", "also_quick"], 1.0)
    assert got == ["result for quick", "result for also_quick"]


async def test_one_budget_covers_the_whole_batch() -> None:
    module = load("ch08", "e08_03_when_all")
    module.cancelled.clear()
    # Each of these finishes well inside 0.1 s on its own, and together
    # they still do, because they run at once rather than in turn.
    got = await module.fetch_all(["quick", "also_quick"], 0.1)
    assert len(got) == 2


async def test_overrunning_the_budget_raises_timeout() -> None:
    module = load("ch08", "e08_03_when_all")
    module.cancelled.clear()
    with pytest.raises(TimeoutError):
        await module.fetch_all(["quick", "slow"], 0.1)


async def test_nothing_is_left_running_after_the_budget_passes() -> None:
    module = load("ch08", "e08_03_when_all")
    module.cancelled.clear()
    with pytest.raises(TimeoutError):
        await module.fetch_all(["quick", "slow"], 0.1)
    # The orphan this catches is the one gather leaves behind: the fetch
    # nobody is waiting for any more, still holding its connection.
    assert "slow" in module.cancelled, (
        "the slow fetch was never cancelled, so it is still running with "
        "nobody waiting for it"
    )
