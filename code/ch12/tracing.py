"""Tracing, and the one processor that ties a log line to a span.

Run it from code/:

    uv run python ch12/tracing.py

Three nouns, and you already have all three under different names: a
TracerProvider is what you configure once (an ActivityListener and its
exporters), a Tracer is what a module holds (an ActivitySource), and a
span is what you open around some work (an Activity).

The part worth copying is `add_trace_ids`. Put it in the processor chain
from ch12/log_setup.py and every log line written inside a span carries
the identifiers the trace was recorded under, so a line in a log search
and a span in a trace viewer are one click apart.

The demo pins the identifiers so the printed output is reproducible; a
real provider generates them randomly, which is the whole point of the
56 random bits the specification asks for.
"""

import sys

import structlog
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, SpanExporter
from opentelemetry.sdk.trace.id_generator import IdGenerator
from structlog.types import EventDict, WrappedLogger


def add_trace_ids(
    _logger: WrappedLogger, _name: str, event: EventDict
) -> EventDict:
    """Stamp the current span's identifiers, when there is one."""
    context = trace.get_current_span().get_span_context()
    if context.is_valid:
        event["trace_id"] = format(context.trace_id, "032x")
        event["span_id"] = format(context.span_id, "016x")
    return event


class FixedIds(IdGenerator):
    """A generator with the randomness taken out, so the demo repeats."""

    def generate_trace_id(self) -> int:
        return 0x4D9A1C77E1B34F0A9C2D6E5F0A1B2C3D

    def generate_span_id(self) -> int:
        return 0x00A1B2C3D4E5F601


def configure_tracing(
    service_name: str,
    exporter: SpanExporter | None = None,
    id_generator: IdGenerator | None = None,
) -> TracerProvider:
    """Install a provider. Without a service name every span is anonymous."""
    provider = TracerProvider(
        # Miss this out and the SDK files every span your service ever
        # emits under the literal string "unknown_service".
        resource=Resource.create({"service.name": service_name}),
        id_generator=id_generator,
    )
    if exporter is not None:
        provider.add_span_processor(SimpleSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    return provider


def main() -> int:
    configure_tracing("ops-copilot", id_generator=FixedIds())
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            add_trace_ids,
            structlog.processors.JSONRenderer(sort_keys=True),
        ]
    )
    log = structlog.get_logger()
    tracer = trace.get_tracer(__name__)

    log.info("outside any span")
    with tracer.start_as_current_span("charge") as span:
        span.set_attribute("order.id", 7)
        log.info("inside the span")
    return 0


if __name__ == "__main__":
    sys.exit(main())
