#!/usr/bin/env python3
"""E4: what one blocking call costs, in the TPL-against-asyncio framing.

The .NET reader's protection against a blocking call is the thread pool.
`Task.Run(() => Thread.Sleep(100))` four times over occupies four pool
threads out of hundreds, the four sleeps overlap, and the work finishes in
about the time one of them takes. Nothing else in the process notices.

There is no pool under an event loop. One thread runs every coroutine, so
this script measures the two consequences that follow and that a .NET
mental model does not predict:

  * blocking calls do not overlap WITH EACH OTHER. K of them take K times as
    long on the loop's own thread as they do off it.
  * every co-resident coroutine pays for all of them, in full, whatever it
    was doing -- which is the bystander cost.

The LangChain book's chapter 3 measures the single-offender case in depth
and this script does not repeat it; what is here is the additivity in K,
which is the half a thread pool would have hidden.

WHY NOTHING MEASURED IS COMMITTED. `make verify` re-runs every script under
measure/ and fails when a committed value moves, and CI runs it on a machine
nobody controls -- so a timing in milliseconds would fail the build on its
first green run. Every value written out is therefore EXACT ARITHMETIC ON
THE INPUTS: the predicted serialised cost is K * B because that is what one
thread means, and the bounds are fractions of it. The measurement's job is
to be ASSERTED against those bounds, not to be printed. A machine that
disagrees fails this script loudly rather than drifting a digit quietly,
which is the sibling books' rule (assert the invariant, never the
observation) applied to a stopwatch.

The bounds are one-sided in the direction that a slow machine makes EASIER
to clear: a floor under the degradation, a ceiling over the threaded cost.
A loaded CI runner can only block harder.

Run from code/:   uv run python measure/e04_blocking.py
"""

from __future__ import annotations

import asyncio
import statistics
import sys
import time
from collections.abc import Callable, Coroutine
from pathlib import Path
from typing import Any

# create_task takes a coroutine and not merely an awaitable, and pyright is
# strict enough to say so: Callable[[], Awaitable[None]] is rejected here.
Offender = Callable[[], Coroutine[Any, Any, None]]

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "figures" / "values" / "e04.tex"

INNOCENT = 8        # coroutines minding their own business
WAIT_MS = 20        # what each of them awaits
OFFENDERS = 4       # coroutines that take BLOCK_MS of CPU-free wall time
BLOCK_MS = 100      # each offender's stretch of it
TRIALS = 5          # median of, after one discarded warm-up


class Result:
    """One scenario's two numbers, in milliseconds."""

    def __init__(self, offenders_ms: float, worst_innocent_ms: float) -> None:
        self.offenders_ms = offenders_ms
        self.worst_innocent_ms = worst_innocent_ms


async def innocent(latencies: list[float]) -> None:
    """Await WAIT_MS and record how long that actually took."""
    start = time.perf_counter()
    await asyncio.sleep(WAIT_MS / 1000)
    latencies.append((time.perf_counter() - start) * 1000)


async def offender_awaits() -> None:
    """The well-behaved shape: hands the loop back for the duration."""
    await asyncio.sleep(BLOCK_MS / 1000)


async def offender_blocks() -> None:
    """The incident: a synchronous call inside a coroutine."""
    time.sleep(BLOCK_MS / 1000)


async def offender_threaded() -> None:
    """The fix: the same synchronous call, off the loop's thread."""
    await asyncio.to_thread(time.sleep, BLOCK_MS / 1000)


async def scenario(offender: Offender) -> Result:
    """Start the innocents and the offenders together; time both halves."""
    latencies: list[float] = []
    innocents = [asyncio.create_task(innocent(latencies))
                 for _ in range(INNOCENT)]
    started = time.perf_counter()
    offending = [asyncio.create_task(offender()) for _ in range(OFFENDERS)]
    await asyncio.gather(*offending)
    offenders_ms = (time.perf_counter() - started) * 1000
    await asyncio.gather(*innocents)
    return Result(offenders_ms, max(latencies))


async def measure() -> dict[str, Result]:
    shapes: dict[str, Offender] = {
        "clean": offender_awaits,
        "blocking": offender_blocks,
        "threaded": offender_threaded,
    }
    samples: dict[str, list[Result]] = {name: [] for name in shapes}
    for trial in range(TRIALS + 1):
        for name, shape in shapes.items():
            result = await scenario(shape)
            if trial:          # the first pass warms the thread pool up
                samples[name].append(result)
    return {
        name: Result(
            statistics.median(r.offenders_ms for r in runs),
            statistics.median(r.worst_innocent_ms for r in runs),
        )
        for name, runs in samples.items()
    }


def main() -> int:
    measured = asyncio.run(measure())
    clean, blocking, threaded = (
        measured["clean"], measured["blocking"], measured["threaded"]
    )

    # Exact arithmetic on the inputs. One thread cannot overlap two blocking
    # calls, so K of them cost K * B and nothing about the machine changes
    # that; the bounds are fractions of the same product.
    serial_ms = OFFENDERS * BLOCK_MS
    added_floor_ms = int(serial_ms * 0.9)
    threaded_ceiling_ms = BLOCK_MS // 2

    # ...and the assertions the measurement has to clear.
    added = blocking.worst_innocent_ms - clean.worst_innocent_ms
    if added < added_floor_ms:
        raise SystemExit(
            f"E4: a blocking offender added {added:.0f} ms to the worst "
            f"innocent coroutine, under the {added_floor_ms} ms floor this "
            f"script commits. Either the loop absorbed it -- which would "
            f"refute the chapter -- or the machine is too slow to time."
        )
    added_threaded = threaded.worst_innocent_ms - clean.worst_innocent_ms
    if added_threaded > threaded_ceiling_ms:
        raise SystemExit(
            f"E4: moving the blocking call to a thread still added "
            f"{added_threaded:.0f} ms, over the {threaded_ceiling_ms} ms "
            f"ceiling. On a machine this loaded the comparison says nothing."
        )
    if blocking.offenders_ms < serial_ms * 0.9:
        raise SystemExit(
            f"E4: {OFFENDERS} blocking calls of {BLOCK_MS} ms took "
            f"{blocking.offenders_ms:.0f} ms, so they overlapped. That "
            f"cannot happen on one thread."
        )
    if threaded.offenders_ms > serial_ms / 2:
        raise SystemExit(
            f"E4: {OFFENDERS} calls through to_thread took "
            f"{threaded.offenders_ms:.0f} ms and did not overlap. Check the "
            f"default executor's worker count against OFFENDERS."
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        "% Generated by code/measure/e04_blocking.py --- do not edit.\n"
        f"\\pyval{{e04.innocent}}{{{INNOCENT}}}\n"
        f"\\pyval{{e04.wait.ms}}{{{WAIT_MS}}}\n"
        f"\\pyval{{e04.offenders}}{{{OFFENDERS}}}\n"
        f"\\pyval{{e04.block.ms}}{{{BLOCK_MS}}}\n"
        f"\\pyval{{e04.serial.ms}}{{{serial_ms}}}\n"
        f"\\pyval{{e04.added.floor.ms}}{{{added_floor_ms}}}\n"
        f"\\pyval{{e04.threaded.ceiling.ms}}{{{threaded_ceiling_ms}}}\n"
        f"\\pyval{{e04.trials}}{{{TRIALS}}}\n",
        encoding="utf8",
    )
    print(
        f"  e04: {OFFENDERS} x {BLOCK_MS} ms blocking took "
        f"{blocking.offenders_ms:.0f} ms on the loop and "
        f"{threaded.offenders_ms:.0f} ms off it; the worst innocent "
        f"coroutine went {clean.worst_innocent_ms:.0f} -> "
        f"{blocking.worst_innocent_ms:.0f} -> "
        f"{threaded.worst_innocent_ms:.0f} ms"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
