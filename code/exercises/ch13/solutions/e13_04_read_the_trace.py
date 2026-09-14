"""Reference solution for exercise 13.4."""

from __future__ import annotations

from collections import Counter

from trace_assert import Trace


def unanswered(trace: Trace) -> tuple[str, ...]:
    """The models called more often than they answered, in call order,
    each named once."""
    calls = Counter(trace.names("model_call"))
    results = Counter(trace.names("model_result"))
    short = calls - results
    # Counter subtraction drops anything at or below zero, which is
    # exactly "answered at least as often as it was called".
    seen: list[str] = []
    for name in trace.names("model_call"):
        if short[name] and name not in seen:
            seen.append(name)
    return tuple(seen)


def spend(trace: Trace) -> tuple[int, int]:
    """Total input and output tokens over every result in the trace."""
    totals = [0, 0]
    for event in trace.of_kind("model_result"):
        for index, key in enumerate(("input_tokens", "output_tokens")):
            value = event.payload.get(key, 0)
            if isinstance(value, int):
                totals[index] += value
    return totals[0], totals[1]
