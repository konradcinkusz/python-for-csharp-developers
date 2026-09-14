"""Exercise 8.3 -- get a blocking call off the loop's thread.

`render_report` is synchronous and slow: it is a CPU-free wait, the kind a
library does when it shells out, reads a file or calls a driver that has no
async form. Calling it from inside a coroutine stops every other coroutine
on the loop for its whole duration, because there is only one thread.

Make `report` return exactly what `render_report` returns, without the loop
going quiet while it runs. The test runs a heartbeat coroutine alongside and
counts its ticks: a blocked loop cannot tick.

Do not edit `render_report`, and do not replace it with a sleep -- the point
is that you cannot always rewrite the slow thing.
"""

import time

BLOCK_SECONDS = 0.4


def render_report(rows: int) -> str:
    """A synchronous call you do not own. Do not edit this."""
    time.sleep(BLOCK_SECONDS)
    return f"report of {rows} rows"


async def report(rows: int) -> str:
    """Return render_report(rows) without starving the loop."""
    raise NotImplementedError("your turn: replace this line")
