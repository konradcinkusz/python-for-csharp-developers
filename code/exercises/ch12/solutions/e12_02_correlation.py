"""Reference solution for exercise 12.2."""

from __future__ import annotations

import contextvars


class RequestContext:
    """Holds the current request's identifier, one per context."""

    # The whole change. A ContextVar is AsyncLocal<T>: every task gets a
    # copy of its parent's context when it is created, so a set() here
    # cannot be seen by a sibling task and cannot leak back to the caller.
    _current: contextvars.ContextVar[str] = contextvars.ContextVar(
        "request_id", default="none"
    )

    @classmethod
    def set(cls, request_id: str) -> None:
        cls._current.set(request_id)

    @classmethod
    def get(cls) -> str:
        return cls._current.get()

    @classmethod
    def clear(cls) -> None:
        cls._current.set("none")
