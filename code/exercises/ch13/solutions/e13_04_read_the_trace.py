"""Reference solution for exercise 13.4."""

from __future__ import annotations

from collections import Counter

from trace_assert import Event, Trace


def _model(event: Event) -> str:
    """The model a model event names.

    `tags` is `dict[str, object]`, so the value has to be narrowed before
    it can be used as a `str` -- which is chapter 3's lesson arriving in an
    exercise about chapter 13. An event with no `model` tag is malformed
    and is counted under the empty name rather than crashing: neither
    function may assume the trace is well formed.
    """
    value = event.tags.get("model")
    return value if isinstance(value, str) else ""


def unanswered(trace: Trace) -> tuple[str, ...]:
    """The models called more often than they answered, in call order,
    each named once."""
    calls = Counter(_model(e) for e in trace.events_named("model_call"))
    results = Counter(_model(e) for e in trace.events_named("model_result"))
    short = calls - results
    # Counter subtraction drops anything at or below zero, which is
    # exactly "answered at least as often as it was called".
    seen: list[str] = []
    for event in trace.events_named("model_call"):
        name = _model(event)
        if short[name] and name not in seen:
            seen.append(name)
    return tuple(seen)


def spend(trace: Trace) -> tuple[int, int]:
    """Total input and output tokens over every result in the trace."""
    totals = [0, 0]
    for event in trace.events_named("model_result"):
        for index, key in enumerate(("input_tokens", "output_tokens")):
            value = event.tags.get(key, 0)
            if isinstance(value, int):
                totals[index] += value
    return totals[0], totals[1]
