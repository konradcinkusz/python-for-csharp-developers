"""The logging bootstrap: one line is one dict, and one place configures it.

Run it from code/:

    uv run python ch12/log_setup.py

`configure_logging` is the whole of it and it is meant to be copied. It
does two things the standard library will not do for you: it renders every
record as one JSON object, and it puts the SAME pre-chain in front of
records that arrived through `logging` rather than through structlog -- so
a line written by a library you did not write still carries the request
identifier you bound.

The demo asks for no timestamp, which is why its output fits this page.
That is not only a page-width convenience: under a collector that stamps
every line it receives -- Docker, journald, most hosted log services -- the
application's own timestamp is a second, slightly different answer to a
question somebody else has already answered. Keep the default when you are
writing to a file.
"""

import logging
import sys
from collections.abc import Sequence
from typing import TextIO

import structlog
from structlog.types import Processor

DEFAULT_TIMESTAMPER: Processor = structlog.processors.TimeStamper(
    fmt="iso", utc=True
)


def configure_logging(
    stream: TextIO | None = None,
    *,
    timestamper: Processor | None = DEFAULT_TIMESTAMPER,
) -> None:
    """Send every log line, from anywhere, to `stream` as one JSON object."""
    shared: Sequence[Processor] = [
        # First, or a line rendered before the merge carries no context.
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        *([timestamper] if timestamper is not None else []),
    ]
    structlog.configure(
        processors=[
            *shared,
            # Hands the event dict on to the stdlib handler below instead
            # of rendering it here, which is what lets ONE renderer serve
            # both structlog's records and `logging`'s.
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    handler = logging.StreamHandler(stream or sys.stdout)
    handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            # The same pre-chain, for records that never met structlog.
            foreign_pre_chain=shared,
            processors=[
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                structlog.processors.JSONRenderer(sort_keys=True),
            ],
        )
    )
    root = logging.getLogger()
    # Replace, do not append: whatever logged at import time left a handler
    # here, and adding to it prints every line twice.
    root.handlers = [handler]
    root.setLevel(logging.INFO)


def main() -> int:
    configure_logging(timestamper=None)
    log = structlog.get_logger("ops")

    structlog.contextvars.bind_contextvars(request_id="4c1f")
    log.info("charge ok", order_id=7)
    # Not ours. A library, using the standard library, knowing nothing
    # about structlog and nothing about the request identifier.
    logging.getLogger("httpx").warning("retrying %s", "POST /charge")
    structlog.contextvars.clear_contextvars()

    log.info("worker idle")
    return 0


if __name__ == "__main__":
    sys.exit(main())
