"""Exercise 13.4 -- why a model call is two events and not one.

`Recorder` writes a `model_call` when the request leaves and a
`model_result` when the reply arrives. One event written afterwards would
be simpler and could not represent the case you most want to find: a call
that never came back.

Write both functions over a `Trace`. Neither may assume the trace is
well formed -- that is the point of having it.
"""

from __future__ import annotations

from trace_assert import Trace


def unanswered(trace: Trace) -> tuple[str, ...]:
    """The models called more often than they answered, in call order,
    each named once."""
    raise NotImplementedError("your turn: replace this line")


def spend(trace: Trace) -> tuple[int, int]:
    """Total input and output tokens over every result in the trace."""
    raise NotImplementedError("your turn: replace this line")
