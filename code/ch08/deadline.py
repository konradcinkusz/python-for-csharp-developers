"""A deadline is a cancellation with a nicer name at the boundary.

Run it from the repository root:

    cd code && uv run python ch08/deadline.py

asyncio.timeout cancels the work inside it when the deadline passes, so the
body sees CancelledError -- the same exception chapter 8 has just spent a
section on -- and the CALLER sees TimeoutError. The conversion happens at
the context manager's edge, which is exactly why a body that swallows a
cancellation breaks its own timeout.

The last two lines are read off the installed httpx rather than written
down: a client constructed with no arguments already carries a deadline,
and it is a short one.
"""

import asyncio

import httpx

seen_inside: list[str] = []


async def slow() -> str:
    try:
        await asyncio.sleep(10)
    except BaseException as exc:
        seen_inside.append(type(exc).__name__)
        raise
    return "finished"


async def swallows_its_own_deadline() -> str:
    try:
        await asyncio.sleep(10)
    except asyncio.CancelledError:
        return "swallowed the cancellation the deadline sent"
    return "finished inside the deadline"


async def main() -> None:
    try:
        async with asyncio.timeout(0.05):
            await slow()
    except TimeoutError as exc:
        print(f"the caller sees:      {type(exc).__name__}")
    print(f"the body saw:         {seen_inside[0]}")
    print(f"asyncio.TimeoutError is the builtin TimeoutError: "
          f"{asyncio.TimeoutError is TimeoutError}")

    try:
        async with asyncio.timeout(0.05):
            print(f"a body that swallows: "
                  f"{await swallows_its_own_deadline()}")
    except TimeoutError:
        print("a body that swallows: the deadline still fired")
    except RuntimeError as exc:
        print(f"a body that swallows: RuntimeError: {exc}")

    async with httpx.AsyncClient() as client:
        deadline = client.timeout
        print(f"httpx.AsyncClient() default timeout: {deadline}")
        print(f"  connect {deadline.connect}, read {deadline.read}, "
              f"write {deadline.write}, pool {deadline.pool}")


if __name__ == "__main__":
    asyncio.run(main())
