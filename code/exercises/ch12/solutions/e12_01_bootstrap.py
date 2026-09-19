"""Reference solution for exercise 12.1."""

from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import TextIO

import structlog
from structlog.types import Processor


def configure_logging(stream: TextIO) -> None:
    """Route structlog AND `logging` to `stream`, as JSON, with context."""
    shared: Sequence[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
    ]
    structlog.configure(
        processors=[
            *shared,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=False,
    )
    handler = logging.StreamHandler(stream)
    handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=shared,
            processors=[
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                structlog.processors.JSONRenderer(sort_keys=True),
            ],
        )
    )
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(logging.INFO)
