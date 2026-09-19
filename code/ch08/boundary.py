"""The sync boundary: where async code starts, and what cannot cross it.

Run it from the repository root:

    cd code && uv run python ch08/boundary.py

Python has no `async Main`. `await` outside a function is a SyntaxError, so
something synchronous has to start the loop, and that something is
asyncio.run -- called once, at the top, and never from inside a coroutine.

The other two lines are the .Result habit meeting a runtime that does not
have it. There is no blocking wait on a Task from inside the loop: asking
an unfinished Task for its value does not block and does not deadlock, it
refuses.
"""

import asyncio


async def answer() -> int:
    await asyncio.sleep(0.01)
    return 42


async def main() -> None:
    task = asyncio.create_task(answer())

    try:
        task.result()
    except asyncio.InvalidStateError as exc:
        print("task.result() before it finishes:")
        print(f"  {type(exc).__name__}: {exc}")

    # Built first and closed explicitly: asyncio.run refuses it, which
    # leaves a coroutine nobody awaited, which warns when it is collected.
    orphan = answer()
    try:
        asyncio.run(orphan)
    except RuntimeError as exc:
        print("asyncio.run() inside a running loop:")
        print(f"  {type(exc).__name__}: {exc}")
    finally:
        orphan.close()

    print(f"task.result() after awaiting it: {await task}")

    try:
        compile("await answer()", "<stdin>", "exec")
    except SyntaxError as exc:
        print(f"await at module level: {type(exc).__name__}: {exc.msg}")

    print(f"asyncio has ConfigureAwait: {hasattr(asyncio, 'ConfigureAwait')}")


if __name__ == "__main__":
    # The one synchronous call in the file, and the only place the loop is
    # created. asyncio.run closes it again on the way out.
    asyncio.run(main())
