"""What a run leaves behind: an Event, a Trace of them, and a Recorder.

The model was the whole package at the scaffold, in __init__.py. Chapter 11
splits it out, because stage 01 adds two more modules beside it and a
package whose every name lives in __init__.py is a module wearing a
directory's clothes.

The split that matters is Recorder against Trace. A Recorder is MUTABLE and
belongs to the run: the code under test appends to it while it works. A
Trace is IMMUTABLE and belongs to the assertions: it is the evidence, and an
assertion that could edit the evidence is not an assertion. That is why
Trace holds a tuple, and it is why `recorder.trace` builds a new one rather
than handing out the recorder's own list.
"""

from __future__ import annotations

from dataclasses import dataclass, field

__all__ = ["Event", "Recorder", "Trace"]

# The event kinds stage 01 knows about. Deliberately strings rather than an
# Enum: a trace is written by whatever produced it -- chapter 13 writes one
# from a real model call -- and a closed set here would make this package the
# thing that has to change first every time a caller learns a new verb.
TOOL_CALL = "tool_call"
TOOL_RESULT = "tool_result"


def _empty_payload() -> dict[str, object]:
    """A typed empty dict: `default_factory=dict` is dict[Unknown, Unknown]
    to a strict checker, and that is the chapter 3 lesson arriving early."""
    return {}


@dataclass(frozen=True, slots=True)
class Event:
    """One thing the agent did, in the order it did it.

    `kind` is what happened -- `tool_call`, `tool_result`, `model_call`,
    `model_result` -- and `name` is what it happened to. Everything else is
    in `payload`, which is deliberately untyped at this stage: chapter 13
    decides what a model call records.
    """

    kind: str
    name: str
    payload: dict[str, object] = field(default_factory=_empty_payload)

    @property
    def outcome(self) -> str:
        """How the event ended, or `unrecorded`.

        A tool call has a span whether it succeeded or not, so "the write was
        never attempted" and "the write failed" must not look alike in a
        failure message. Where the payload does not say, this says so rather
        than guessing.
        """
        value = self.payload.get("outcome")
        return str(value) if value is not None else "unrecorded"


@dataclass(frozen=True, slots=True)
class Trace:
    """The ordered record of one run.

    A trace is a tuple rather than a list so that an assertion cannot mutate
    the evidence it is asserting over.
    """

    events: tuple[Event, ...] = ()

    def of_kind(self, kind: str) -> tuple[Event, ...]:
        """Every event of one kind, in order."""
        return tuple(e for e in self.events if e.kind == kind)

    def names(self, kind: str) -> tuple[str, ...]:
        """The names of every event of one kind, in order."""
        return tuple(e.name for e in self.of_kind(kind))

    def calls_to(self, tool: str) -> tuple[Event, ...]:
        """Every call to one tool, in order.

        The two assertions in this package are both counts over this, and
        both quote what it returned when they fail.
        """
        return tuple(e for e in self.of_kind(TOOL_CALL) if e.name == tool)


class Recorder:
    """The mutable half: what a run writes into while it runs.

    This is what the `trace` fixture hands a test. The code under test calls
    `tool_call`, and the assertions read `recorder.trace`, which is a fresh
    immutable snapshot every time it is asked for.
    """

    def __init__(self) -> None:
        self._events: list[Event] = []

    def record(
        self, kind: str, name: str, **payload: object
    ) -> None:
        """Append one event of any kind."""
        self._events.append(Event(kind, name, dict(payload)))

    def tool_call(self, name: str, **payload: object) -> None:
        """Append a tool call. The kind every stage 01 assertion counts."""
        self.record(TOOL_CALL, name, **payload)

    def tool_result(self, name: str, **payload: object) -> None:
        """Append the result of a tool call."""
        self.record(TOOL_RESULT, name, **payload)

    @property
    def trace(self) -> Trace:
        """An immutable snapshot of what has been recorded so far."""
        return Trace(tuple(self._events))
