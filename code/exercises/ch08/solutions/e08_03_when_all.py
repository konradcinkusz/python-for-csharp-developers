"""Reference solution for exercise 8.3."""

import asyncio

cancelled: list[str] = []

DELAYS = {"quick": 0.02, "also_quick": 0.03, "slow": 5.0}


async def fetch(name: str) -> str:
    """Pretend to call something. Do not edit this."""
    try:
        await asyncio.sleep(DELAYS[name])
        return f"result for {name}"
    except asyncio.CancelledError:
        cancelled.append(name)
        raise


async def fetch_all(names: list[str], budget: float) -> list[str]:
    """Fetch every name at once, within one budget, cancelling on overrun.

    asyncio.timeout is the CancellationTokenSource: one deadline for the
    whole block, and when it passes every task started inside the group is
    cancelled. The TaskGroup is what makes that true -- gather would let
    the survivors run on with nobody waiting for them.

    Ordering is ours to keep: a TaskGroup hands back Task objects rather
    than results, so the list comprehension holds the positions and the
    results are read out of the tasks afterwards.
    """
    async with asyncio.timeout(budget):
        async with asyncio.TaskGroup() as group:
            tasks = [group.create_task(fetch(name)) for name in names]
    return [task.result() for task in tasks]
