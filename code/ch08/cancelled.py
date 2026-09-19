"""Cancellation is an exception, and it is not the one you would guard.

Run it from the repository root:

    cd code && uv run python ch08/cancelled.py

Four tasks, each cancelled the same way, each catching something different.
The last one catches nothing at all: it never awaits, so there is no point
at which a cancellation could be delivered to it.

CancelledError inherits from BaseException and not from Exception, which
this listing prints rather than asserts. That single line of inheritance is
why `except Exception` -- the clause a .NET engineer has been trained to
treat as the dangerous one -- is the safe clause here.
"""

import asyncio
from collections.abc import Callable, Coroutine
from typing import Any

Cancellable = Callable[[], Coroutine[Any, Any, str]]


async def guards_exception() -> str:
    try:
        await asyncio.sleep(10)
    except Exception:
        return "caught by except Exception"
    return "slept the full ten seconds"


async def guards_baseexception() -> str:
    try:
        await asyncio.sleep(10)
    except BaseException:
        return "caught by except BaseException"
    return "slept the full ten seconds"


async def cleans_up_and_forgets() -> str:
    try:
        await asyncio.sleep(10)
    except asyncio.CancelledError:
        # No `raise`. The cleanup ran and the cancellation stopped here.
        return "caught by except CancelledError, not re-raised"
    return "slept the full ten seconds"


async def never_awaits() -> str:
    total = 0
    for i in range(2_000_000):
        total += i
    return f"ran to completion, summing to {total}"


async def cancel_after_a_moment(coro_fn: Cancellable, name: str) -> None:
    task = asyncio.create_task(coro_fn())
    await asyncio.sleep(0.01)
    task.cancel()
    try:
        outcome = await task
    except asyncio.CancelledError:
        print(f"{name:22} CancelledError reached the caller: cancelled")
    else:
        print(f"{name:22} {outcome}")


async def main() -> None:
    bases = [c.__name__ for c in asyncio.CancelledError.__mro__]
    print(f"CancelledError inherits: {' -> '.join(bases)}")
    print()
    for coro_fn, name in (
        (guards_exception, "except Exception"),
        (guards_baseexception, "except BaseException"),
        (cleans_up_and_forgets, "except CancelledError"),
        (never_awaits, "no await at all"),
    ):
        await cancel_after_a_moment(coro_fn, name)


if __name__ == "__main__":
    asyncio.run(main())
