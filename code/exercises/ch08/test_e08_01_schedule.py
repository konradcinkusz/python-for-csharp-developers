from exercises._loader import load


async def test_returns_one_result_per_name_in_order() -> None:
    module = load("ch08", "e08_01_schedule")
    module.in_flight.clear()
    got = await module.fetch_all(["a", "b", "c"])
    assert got == [
        "result for a",
        "result for b",
        "result for c",
    ]


async def test_all_three_are_in_flight_at_once() -> None:
    module = load("ch08", "e08_01_schedule")
    module.in_flight.clear()
    await module.fetch_all(["a", "b", "c"])
    # A sequential implementation never has more than one running, so the
    # high-water mark is 1. This is the whole difference between building
    # three coroutines and scheduling them.
    assert max(module.in_flight) == 3, (
        f"high-water mark of concurrent fetches was {max(module.in_flight)}, "
        f"so they ran one after another"
    )
