"""Reference solution for exercise 14.2."""

from __future__ import annotations

from trace_assert import Trace


def call_attempts(trace: Trace, tool: str, max_attempts: int) -> None:
    """Assert no call to `tool` exceeded `max_attempts` attempts."""
    calls = trace.calls_to(tool)
    claim = f"call_attempts {tool} max_attempts={max_attempts}"
    if not calls:
        # The whole exercise. A bound on a call that never happened proves
        # nothing, and a check that can only pass is not a check.
        raise AssertionError(
            f"{claim}\n  the tool was never called, so the bound "
            f"proves nothing"
        )
    worst = max(c.attempts for c in calls)
    if worst > max_attempts:
        raise AssertionError(f"{claim}\n  worst call made {worst} attempt(s)")
