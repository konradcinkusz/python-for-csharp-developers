"""Exercise 12.3 -- the one processor that joins a log line to a trace.

A log search and a trace viewer are two different windows onto the same
incident, and what joins them is an identifier appearing in both. The
trace side already has it; the log side does not, until a processor puts
it there.

Write `add_trace_ids` so that a record written INSIDE a span gains
`trace_id` (32 hex characters) and `span_id` (16), and a record written
outside one gains neither -- an invalid span context has an all-zero
identifier, and stamping that on every line is worse than stamping
nothing, because it looks like a real value.
"""

from __future__ import annotations

from structlog.types import EventDict, WrappedLogger


def add_trace_ids(
    _logger: WrappedLogger, _name: str, event: EventDict
) -> EventDict:
    """Stamp the current span's identifiers on `event`, when there is one."""
    raise NotImplementedError("your turn: replace this line")
