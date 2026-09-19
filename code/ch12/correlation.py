"""Where a request identifier lives when two requests share one thread.

Run it from code/:

    uv run python ch12/correlation.py

Two handlers run concurrently. Each stamps its own identifier in two
places -- a module-level variable and a ContextVar -- and reads both back
after an await. Decide what each will report before you run it.

Nothing here is about the event loop itself; chapter 8 owns that. The
question is only where a per-request value can be put so that the other
request cannot see it.
"""

import asyncio
import contextvars
import sys

# The habit that comes across from a static field. One name, one process.
module_level = "unset"

# The one that behaves like AsyncLocal<T>: a value per context, and a task
# gets a copy of its parent's context when it is created.
request_id: contextvars.ContextVar[str] = contextvars.ContextVar(
    "request_id", default="unset"
)


async def handle(name: str, work: float) -> tuple[str, str, str]:
    """Stamp both, do some work, read both back."""
    global module_level  # noqa: PLW0603 -- the habit, on purpose
    module_level = name
    request_id.set(name)
    await asyncio.sleep(work)
    return name, module_level, request_id.get()


async def main() -> None:
    # B finishes first and overwrites what A wrote -- if they share a name.
    results = await asyncio.gather(handle("A", 0.02), handle("B", 0.01))
    print(f"{'handler':>8}  {'module-level':>12}  {'contextvar':>10}")
    for name, seen_module, seen_ctx in results:
        print(f"{name:>8}  {seen_module:>12}  {seen_ctx:>10}")
    # The parent never sees what a child set: a task runs in a COPY.
    print(f"{'caller':>8}  {module_level:>12}  {request_id.get():>10}")


if __name__ == "__main__":
    asyncio.run(main())
    sys.exit(0)
