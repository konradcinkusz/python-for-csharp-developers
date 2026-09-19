"""Two handlers at once, and neither may read the other's identifier."""

from __future__ import annotations

import asyncio
from typing import Any

import pytest

from exercises._loader import load


@pytest.fixture
def ctx() -> Any:
    # ONE load per test. _loader.load() re-executes the module on every
    # call, so loading it inside each handler would hand every coroutine
    # a class object of its own -- and the broken starter would then pass,
    # because two separate classes cannot overwrite each other.
    request_context: Any = load("ch12", "e12_02_correlation").RequestContext
    request_context.clear()
    return request_context


async def handle(ctx: Any, name: str, work: float) -> str:
    """Stamp, wait long enough for the other one to stamp too, read back."""
    ctx.set(name)
    await asyncio.sleep(work)
    return ctx.get()


async def test_each_handler_reads_back_its_own_identifier(
    ctx: Any,
) -> None:
    seen = await asyncio.gather(
        handle(ctx, "A", 0.02), handle(ctx, "B", 0.01)
    )
    assert seen == ["A", "B"]


async def test_the_caller_never_sees_what_a_task_set(ctx: Any) -> None:
    await asyncio.gather(handle(ctx, "A", 0.0))
    assert ctx.get() == "none"


async def test_a_child_task_cannot_overwrite_the_caller(
    ctx: Any,
) -> None:
    # Every test here must fail against the starter, so this one checks
    # isolation too rather than a plain set/get round trip, which the
    # broken version passes.
    ctx.set("caller")
    await asyncio.gather(handle(ctx, "child", 0.0))
    assert ctx.get() == "caller"
