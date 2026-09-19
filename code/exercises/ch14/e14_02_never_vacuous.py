"""Exercise 14.2 -- the assertion that can only pass.

`call_attempts(trace, tool, max_attempts)` says no call to `tool` made more
than `max_attempts` transport attempts. It is how "never a silent retry
loop" stops being a slogan.

Here is the version almost everybody writes first:

    worst = max((c.attempts for c in trace.calls_to(tool)), default=0)
    if worst > max_attempts:
        raise AssertionError(...)

It is green on a run where the tool was never called at all, because the
maximum of nothing is zero and zero is under any bound. So a suite asserting
restraint passes on a run in which nothing happened, which is the one run it
should be loudest about.

Write the version that cannot. The test beside this file asks for both
directions, and one of them is the empty run.
"""

from __future__ import annotations

from trace_assert import Trace


def call_attempts(trace: Trace, tool: str, max_attempts: int) -> None:
    """Assert no call to `tool` exceeded `max_attempts` attempts."""
    raise NotImplementedError("your turn: replace this line")
