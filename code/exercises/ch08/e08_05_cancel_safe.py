"""Exercise 8.5 -- clean up on cancellation and stay cancellable.

`worker` holds something that has to be released: a lease, a lock, a
connection. It already releases it when cancelled, and it is still wrong.

Catching CancelledError and not re-raising it tells the caller the work
finished normally. The task then reports success, `task.cancelled()` is
False, and a deadline wrapped around this worker never fires -- the
cancellation the timeout sent was absorbed, so the timeout reports that
everything completed in time.

Release the lease AND let the cancellation continue. The test checks both.
"""

import asyncio

released: list[str] = []


async def worker(name: str) -> str:
    """Do slow work, releasing the lease if cancelled."""
    try:
        await asyncio.sleep(10)
        return f"{name} finished"
    except asyncio.CancelledError:
        released.append(name)
        return f"{name} cleaned up"
