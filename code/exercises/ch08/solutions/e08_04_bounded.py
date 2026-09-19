"""Reference solution for exercise 8.5."""

import asyncio

peak: list[int] = []
_running = 0


async def call(job: int) -> int:
    """Pretend to call a service that counts what you send it."""
    global _running
    _running += 1
    peak.append(_running)
    try:
        await asyncio.sleep(0.02)
        return job * 2
    finally:
        _running -= 1


async def call_all(jobs: list[int], limit: int) -> list[int]:
    """Call every job, at most `limit` at a time, results in order.

    asyncio.Semaphore is SemaphoreSlim, and `async with` is the WaitAsync
    and Release pair that a `finally` would otherwise have to get right.
    The semaphore goes INSIDE the per-job coroutine rather than around the
    gather: every job is scheduled immediately and then queues for a
    permit, which is what keeps the results in order.
    """
    gate = asyncio.Semaphore(limit)

    async def guarded(job: int) -> int:
        async with gate:
            return await call(job)

    return list(await asyncio.gather(*(guarded(job) for job in jobs)))
