import asyncio

from exercises._loader import load


async def heartbeat(ticks: list[int], stop: asyncio.Event) -> None:
    """Tick every 10 ms until asked to stop. A blocked loop cannot tick."""
    while not stop.is_set():
        await asyncio.sleep(0.01)
        ticks.append(1)


async def test_returns_what_render_report_returns() -> None:
    module = load("ch08", "e08_02_unblock")
    assert await module.report(7) == "report of 7 rows"


async def test_the_loop_keeps_running_while_it_works() -> None:
    module = load("ch08", "e08_02_unblock")
    ticks: list[int] = []
    stop = asyncio.Event()
    beating = asyncio.create_task(heartbeat(ticks, stop))
    await module.report(7)
    stop.set()
    await beating
    # 0.4 s of blocking against a 10 ms heartbeat: a loop that stayed free
    # ticks tens of times, and a loop held by a blocking call ticks once at
    # most. Ten is far below the one and far above the other.
    assert len(ticks) >= 10, (
        f"the heartbeat ticked {len(ticks)} times while the report was "
        f"rendered, so the loop was blocked for the duration"
    )
