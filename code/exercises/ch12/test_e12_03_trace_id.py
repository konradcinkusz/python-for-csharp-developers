"""Inside a span the identifiers appear; outside one they must not."""

from __future__ import annotations

from typing import Any

import pytest
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from structlog.types import EventDict

from exercises._loader import load


@pytest.fixture(scope="module")
def tracer() -> trace.Tracer:
    # set_tracer_provider refuses to replace an existing provider, so the
    # tracer is taken from the provider object rather than from the global.
    return TracerProvider().get_tracer("test")


def stamp() -> EventDict:
    add_trace_ids: Any = load("ch12", "e12_03_trace_id").add_trace_ids
    return add_trace_ids(None, "info", {"event": "work"})


def test_outside_a_span_nothing_is_added() -> None:
    assert stamp() == {"event": "work"}


def test_inside_a_span_both_identifiers_are_added(
    tracer: trace.Tracer,
) -> None:
    with tracer.start_as_current_span("unit"):
        event = stamp()
    assert set(event) == {"event", "span_id", "trace_id"}


def test_the_identifiers_are_hex_of_the_right_width(
    tracer: trace.Tracer,
) -> None:
    with tracer.start_as_current_span("unit") as span:
        event = stamp()
        context = span.get_span_context()
    assert event["trace_id"] == format(context.trace_id, "032x")
    assert event["span_id"] == format(context.span_id, "016x")
    assert len(str(event["trace_id"])) == 32
    assert len(str(event["span_id"])) == 16
