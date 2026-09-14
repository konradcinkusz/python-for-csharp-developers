"""Exercise 12.2 -- a request identifier that two requests cannot share.

`RequestContext` is what a static field looks like when it is carried
across to Python: one name, one process, every request writing over the
previous one. Under any concurrency at all the identifier a handler reads
back is whichever handler wrote last, and the log lines are then filed
under somebody else's request.

Keep the three method names and make the identifier per-context, so that
two coroutines running at the same time each read back their own.
"""

from __future__ import annotations


class RequestContext:
    """Holds the current request's identifier. Wrongly, for now."""

    _current: str = "none"

    @classmethod
    def set(cls, request_id: str) -> None:
        cls._current = request_id

    @classmethod
    def get(cls) -> str:
        return cls._current

    @classmethod
    def clear(cls) -> None:
        cls._current = "none"
