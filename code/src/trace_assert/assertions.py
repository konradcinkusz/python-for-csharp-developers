"""The first two assertions, ported from agent-eval-bench.

The design is not this book's. agent-eval-bench defines its layer-1
assertions in `evals/schema/scenario.schema.json` and evaluates them in
`tests/AbsenceConcierge.Evals/Assertions/AssertionEvaluator.cs`, and the port
follows both rather than reinventing them -- chapter 14 compares three ports
of ONE design, which is only worth doing if the design is the same one.

Two of the set land here, and the schema itself says why they are a pair:
`tool_not_called` is documented there as "half of the two-assertion rule for
a denied path: assert the refusal AND that the call never happened". An
agent that refuses in prose and calls the tool anyway passes the first half
on its own.

Both raise AssertionError rather than returning a verdict, because in pytest
the assertion IS the report. Both set __tracebackhide__, so the failure
points at the reader's test rather than at this file: what a reader needs to
see is which of their events was wrong, not which line of the library
noticed.
"""

from __future__ import annotations

from .model import Trace

__all__ = ["assert_tool_called", "assert_tool_not_called"]


def _seen(trace: Trace) -> str:
    """What the trace does contain, for a message about what it does not."""
    names = trace.names("tool_call")
    return ", ".join(names) if names else "no tool calls at all"


def assert_tool_called(
    trace: Trace,
    tool: str,
    *,
    times: int | None = None,
    at_least: int | None = None,
) -> None:
    """Assert that `tool` was called: exactly `times`, or `at_least` of them.

    `at_least` defaults to 1, so the bare call asserts presence.

    Passing both is refused rather than resolved. The schema refuses it too,
    and gives the reason: the evaluator reads one and ignores the other, so
    an author who wrote both would believe a bound nothing ever checked.
    """
    __tracebackhide__ = True
    if times is not None and at_least is not None:
        raise ValueError(
            "pass times= or at_least=, not both: one of them would be "
            "silently ignored and you would believe a bound that was "
            "never checked"
        )
    count = len(trace.calls_to(tool))
    if times is not None:
        if count != times:
            raise AssertionError(
                f"expected {tool!r} to be called {times} time(s), "
                f"called {count} time(s). Saw: {_seen(trace)}"
            )
        return
    minimum = 1 if at_least is None else at_least
    if count < minimum:
        raise AssertionError(
            f"expected {tool!r} to be called at least {minimum} time(s), "
            f"called {count} time(s). Saw: {_seen(trace)}"
        )


def assert_tool_not_called(trace: Trace, tool: str) -> None:
    """Assert that `tool` was never called.

    The failure names every call it found and how each ended, because a span
    exists whether the call succeeded or not: "the write was never
    attempted" and "the write failed" are different findings and must not
    produce the same message.
    """
    __tracebackhide__ = True
    calls = trace.calls_to(tool)
    if calls:
        outcomes = ", ".join(e.outcome for e in calls)
        raise AssertionError(
            f"expected {tool!r} never to be called, "
            f"called {len(calls)} time(s), outcome(s): {outcomes}"
        )
