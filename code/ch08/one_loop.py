"""One loop, one thread: what a blocking call costs the coroutines beside it.

Run it from the repository root:

    cd code && uv run python ch08/one_loop.py

Experiment E4 (code/measure/e04_blocking.py) is this at measurement
discipline, with the bounds the chapter quotes. This is the version you run
yourself: eight coroutines each ask for 20 ms, four others take 100 ms of
wall time, and the only thing that changes between the three runs is WHERE
those four spend it.

The numbers move from machine to machine and the ordering does not, which
is why the chapter quotes the bounds and this listing prints what your own
machine did.
"""

import asyncio
import time
from collections.abc import Awaitable, Callable

INNOCENT = 8
WAIT_MS = 20
OFFENDERS = 4
BLOCK_MS = 100


async def innocent(latencies: list[float]) -> None:
    start = time.perf_counter()
    await asyncio.sleep(WAIT_MS / 1000)
    latencies.append((time.perf_counter() - start) * 1000)


async def awaits() -> None:
    """Hands the loop back for the duration. Nobody notices."""
    await asyncio.sleep(BLOCK_MS / 1000)


async def blocks() -> None:
    """A synchronous call inside a coroutine. The loop cannot run."""
    time.sleep(BLOCK_MS / 1000)


async def threaded() -> None:
    """The same synchronous call, moved off the loop's own thread."""
    await asyncio.to_thread(time.sleep, BLOCK_MS / 1000)


async def run(offender: Callable[[], Awaitable[None]]) -> tuple[float, float]:
    latencies: list[float] = []
    minding = [asyncio.create_task(innocent(latencies))
               for _ in range(INNOCENT)]
    started = time.perf_counter()
    await asyncio.gather(*[offender() for _ in range(OFFENDERS)])
    spent = (time.perf_counter() - started) * 1000
    await asyncio.gather(*minding)
    return spent, max(latencies)


async def main() -> None:
    print(f"{INNOCENT} coroutines awaiting {WAIT_MS} ms, beside "
          f"{OFFENDERS} taking {BLOCK_MS} ms each")
    print(f"{'':10} {'offenders':>12} {'worst innocent':>16}")
    for name, offender in (("awaits", awaits), ("blocks", blocks),
                           ("to_thread", threaded)):
        spent, worst = await run(offender)
        print(f"{name:10} {spent:9.0f} ms {worst:13.0f} ms")


if __name__ == "__main__":
    asyncio.run(main())
