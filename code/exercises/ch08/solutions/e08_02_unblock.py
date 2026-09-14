"""Reference solution for exercise 8.3."""

import asyncio
import time

BLOCK_SECONDS = 0.4


def render_report(rows: int) -> str:
    """A synchronous call you do not own. Do not edit this."""
    time.sleep(BLOCK_SECONDS)
    return f"report of {rows} rows"


async def report(rows: int) -> str:
    """Return render_report(rows) without starving the loop.

    to_thread is Task.Run with a much smaller pool behind it: the default
    executor has min(32, cpu_count + 4) workers and does not grow the way
    the .NET thread pool does. It is the right tool for a blocking call
    that waits, and the wrong one for a thousand of them at once.
    """
    return await asyncio.to_thread(render_report, rows)
