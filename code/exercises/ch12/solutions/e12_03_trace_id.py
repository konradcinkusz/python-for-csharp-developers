"""Reference solution for exercise 12.3."""

from __future__ import annotations

from opentelemetry import trace
from structlog.types import EventDict, WrappedLogger


def add_trace_ids(
    _logger: WrappedLogger, _name: str, event: EventDict
) -> EventDict:
    """Stamp the current span's identifiers on `event`, when there is one."""
    context = trace.get_current_span().get_span_context()
    # is_valid is the guard: outside a span the SDK hands back a context
    # whose identifiers are zero, and "trace_id": "000...0" in a log line
    # is a value somebody will eventually try to search for.
    if context.is_valid:
        event["trace_id"] = format(context.trace_id, "032x")
        event["span_id"] = format(context.span_id, "016x")
    return event
