from exercises._loader import load


async def test_every_job_is_called_and_order_is_kept() -> None:
    module = load("ch08", "e08_04_bounded")
    module.peak.clear()
    assert await module.call_all([1, 2, 3, 4, 5, 6], 2) == [
        2, 4, 6, 8, 10, 12,
    ]


async def test_never_more_than_the_limit_in_flight() -> None:
    module = load("ch08", "e08_04_bounded")
    module.peak.clear()
    await module.call_all([1, 2, 3, 4, 5, 6], 2)
    assert max(module.peak) <= 2, (
        f"{max(module.peak)} calls were in flight at once against a limit "
        f"of 2"
    )


async def test_the_limit_is_used_rather_than_serialised() -> None:
    module = load("ch08", "e08_04_bounded")
    module.peak.clear()
    await module.call_all([1, 2, 3, 4, 5, 6], 2)
    # A loop that awaits each call in turn also never exceeds the limit,
    # and is not what was asked for.
    assert max(module.peak) == 2, (
        f"only {max(module.peak)} call was ever in flight, so the jobs ran "
        f"one at a time"
    )
