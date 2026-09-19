"""Task.WhenAll has two Python spellings, and they differ when one fails.

Run it from the repository root:

    cd code && uv run python ch08/whenall.py

Both run their coroutines concurrently and both are the same speed. The
difference is what happens to the SIBLINGS of a coroutine that raises:
gather leaves them running with nobody waiting for them, TaskGroup cancels
them. The log below is printed in the order the events happened, so the
orphan's last line arrives after the caller has already handled the error.
"""

import asyncio

log: list[str] = []


async def fails() -> None:
    await asyncio.sleep(0.02)
    raise ValueError("boom")


async def sibling() -> None:
    try:
        await asyncio.sleep(0.15)
        log.append("sibling finished, long after the caller moved on")
    except asyncio.CancelledError:
        log.append("sibling cancelled")
        raise


async def with_gather() -> None:
    try:
        await asyncio.gather(fails(), sibling())
    except ValueError as exc:
        log.append(f"caller caught {type(exc).__name__}")
    await asyncio.sleep(0.2)


async def with_taskgroup() -> None:
    try:
        async with asyncio.TaskGroup() as group:
            group.create_task(fails())
            group.create_task(sibling())
    except* ValueError as group_exc:
        inner = [type(e).__name__ for e in group_exc.exceptions]
        log.append(f"caller caught ExceptionGroup containing {inner}")
    await asyncio.sleep(0.2)


async def main() -> None:
    for name, shape in (("gather", with_gather),
                        ("TaskGroup", with_taskgroup)):
        log.clear()
        await shape()
        print(f"{name}:")
        for line in log:
            print(f"  {line}")


if __name__ == "__main__":
    asyncio.run(main())
