"""Reference solution for exercise 8.1."""

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
    """Return one result per name, in order, with all of them in flight.

    gather schedules every coroutine it is given and returns their results
    in the order the ARGUMENTS were passed, not the order they finished --
    which is what lets the caller keep using positions.

    A TaskGroup would do as well here and would cancel the siblings if one
    of them raised. Nothing raises in this exercise, so the two are the
    same; chapter 8 is about the case where they are not.
    """
    return list(await asyncio.gather(*(fetch(name) for name in names)))
