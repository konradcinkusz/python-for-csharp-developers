"""Exercise 12.1 -- one renderer for your lines and everybody else's.

The service emits two kinds of log record: the ones you write through
structlog, and the ones a library writes through the standard `logging`
module. They must come out of the same handler, as JSON, and BOTH must
carry whatever was bound with bind_contextvars.

Finish `configure_logging` so that the test passes. ch12/log_setup.py is
the worked version; write this one before you read it.
"""

from __future__ import annotations

from typing import TextIO


def configure_logging(stream: TextIO) -> None:
    """Route structlog AND `logging` to `stream`, as JSON, with context."""
    raise NotImplementedError("your turn: replace this line")
