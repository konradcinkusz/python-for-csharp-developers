import asyncio

import pytest

from exercises._loader import load


async def test_the_lease_is_released_on_cancellation() -> None:
    module = load("ch08", "e08_05_cancel_safe")
    module.released.clear()
    task = asyncio.create_task(module.worker("lease-1"))
    await asyncio.sleep(0.01)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert module.released == ["lease-1"]


async def test_the_task_actually_ends_cancelled() -> None:
    module = load("ch08", "e08_05_cancel_safe")
    module.released.clear()
    task = asyncio.create_task(module.worker("lease-2"))
    await asyncio.sleep(0.01)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert task.cancelled(), (
        "the task reported success after being cancelled, so whoever "
        "cancelled it believes the work completed"
    )


async def test_a_deadline_around_the_worker_fires() -> None:
    module = load("ch08", "e08_05_cancel_safe")
    module.released.clear()
    # The consequence a caller actually meets: a swallowed cancellation is
    # a timeout that silently does not fire.
    with pytest.raises(TimeoutError):
        async with asyncio.timeout(0.05):
            await module.worker("lease-3")
