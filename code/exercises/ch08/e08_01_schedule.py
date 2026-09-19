"""Exercise 8.1 -- make three coroutines overlap.

`fetch` is already a coroutine function. Calling it three times in a row
builds three coroutine objects and runs none of them: a coroutine is cold.
Awaiting each one as you build it runs them one after another, which is
the shape most people write first and is no faster than a synchronous loop.

Return the three results, in the order the names were given, with all three
running at once. The test watches how many are in flight at the same time,
so a sequential implementation fails it even though its results are right.
"""

import asyncio

in_flight: list[int] = []
_running = 0


async def fetch(name: str) -> str:
    """Pretend to call something over a network. Do not edit this."""
    global _running
    _running += 1
    in_flight.append(_running)
    try:
        await asyncio.sleep(0.05)
        return f"result for {name}"
    finally:
        _running -= 1


async def fetch_all(names: list[str]) -> list[str]:
    """Return one result per name, in order, with all of them in flight."""
    raise NotImplementedError("your turn: replace this line")
