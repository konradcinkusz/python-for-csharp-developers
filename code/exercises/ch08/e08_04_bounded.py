"""Exercise 8.5 -- bound the concurrency, the way SemaphoreSlim does.

`gather` and `TaskGroup` start everything at once. Twenty requests against
a service that tolerates four is not concurrency, it is a load test with
your own name on it, and the failure arrives as their rate limiter rather
than as your exception.

Run every job, return the results in order, and never have more than
`limit` of them in flight. `peak` is recorded for you; the test reads it.
"""

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
    """Call every job, at most `limit` at a time, results in order."""
    raise NotImplementedError("your turn: replace this line")
