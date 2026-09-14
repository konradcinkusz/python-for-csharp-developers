"""A coroutine is cold. A Task is hot. Everything else follows from that.

Run it from the repository root:

    cd code && uv run python ch08/cold.py

Four facts, each read from the interpreter rather than written down:
calling a coroutine function runs nothing; create_task schedules rather
than starts; forgetting the await is a warning and not an error; and a
coroutine cannot be awaited twice, where a Task can be.
"""

import asyncio
import gc
import warnings

ran: list[str] = []


async def work(tag: str) -> str:
    ran.append(tag)
    await asyncio.sleep(0)
    return tag


async def main() -> None:
    ran.clear()
    pending = work("A")
    print(f"calling work('A') returned a {type(pending).__name__}")
    print(f"  and the body has run: {bool(ran)}")
    await pending
    print(f"  after awaiting it, the body has run: {bool(ran)}")

    ran.clear()
    task = asyncio.create_task(work("B"))
    print(f"after create_task the body has run: {bool(ran)}")
    await asyncio.sleep(0)
    print(f"  after the caller yields once: {bool(ran)}")
    await task

    # A coroutine nobody awaited is garbage collected, and complains on the
    # way out. Captured here rather than left to reach stderr, because the
    # point is to show you the text, not to print a warning.
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        forgotten = work("C")
        del forgotten
        gc.collect()
    for entry in caught:
        print(f"forgetting the await: {entry.category.__name__}: "
              f"{entry.message}")

    # A Task is a handle on work already under way, so awaiting it twice is
    # reading the same answer twice. A coroutine is the work itself.
    once = work("D")
    await once
    try:
        await once
    except RuntimeError as exc:
        print("awaiting the same coroutine twice:")
        print(f"  {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    asyncio.run(main())
