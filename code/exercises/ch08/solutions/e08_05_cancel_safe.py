"""Reference solution for exercise 8.5."""

import asyncio

released: list[str] = []


async def worker(name: str) -> str:
    """Do slow work, releasing the lease if cancelled.

    The bare `raise` is the whole fix, and it is `throw;` rather than
    `throw ex;` -- it continues the exception that is already in flight
    with its traceback intact. A `finally:` would do the same job here
    without naming the exception at all, and is the better shape when the
    cleanup is the same whether or not the work was cancelled.
    """
    try:
        await asyncio.sleep(10)
        return f"{name} finished"
    except asyncio.CancelledError:
        released.append(name)
        raise
