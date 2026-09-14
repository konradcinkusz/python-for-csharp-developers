"""Exercise 8.3 -- port a WhenAll with a CancellationToken.

This is the C# the chapter asks you to translate:

    using var cts = new CancellationTokenSource(budget);
    var tasks = names.Select(n => FetchAsync(n, cts.Token));
    var results = await Task.WhenAll(tasks);

Three things have to survive the crossing:

  * every fetch runs concurrently, and the results come back in the order
    the names were given;
  * one budget covers the whole batch, not each fetch separately;
  * when the budget runs out, no fetch is left running -- which is the
    part `gather` does not give you and the one the test checks.

`fetch` takes its own time per name, and `cancelled` records every name
whose fetch was stopped. Raise TimeoutError if the budget runs out.
"""

import asyncio

cancelled: list[str] = []

DELAYS = {"quick": 0.02, "also_quick": 0.03, "slow": 5.0}


async def fetch(name: str) -> str:
    """Pretend to call something. Do not edit this."""
    try:
        await asyncio.sleep(DELAYS[name])
        return f"result for {name}"
    except asyncio.CancelledError:
        cancelled.append(name)
        raise


async def fetch_all(names: list[str], budget: float) -> list[str]:
    """Fetch every name at once, within one budget, cancelling on overrun."""
    raise NotImplementedError("your turn: replace this line")
