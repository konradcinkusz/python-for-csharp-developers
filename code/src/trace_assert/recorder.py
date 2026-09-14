"""Stage 02: turning a model call into evidence an assertion can grade.

Chapter 13 records a call; chapter 14 grades it. This is the join, and it
is deliberately small: a recorder that knows how to write one kind of
event, against the trace model in `trace.py`, which is the specification's
and not this book's.

Two events per call, not one. A call that never came back is the case most
worth being able to find, and a single event written after the reply cannot
represent it -- there is nothing to write when nothing arrives.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .trace import Event, Trace

__all__ = ["Recorder"]


def _no_events() -> list[Event]:
    """A typed empty list, for the reason `_no_tags` is a typed empty dict:
    `default_factory=list` is list[Unknown] to a strict checker, which is
    chapter 3's lesson arriving in the package the whole book builds."""
    return []


@dataclass(slots=True)
class Recorder:
    """Collects events in order, and hands back a Trace nothing can edit.

    The event's `name` is the KIND -- `model_call`, `model_result` -- and
    the model is a tag. That is the way round the assertions read: they ask
    `events_named("model_call")` and `Span.of_event("model_call")`, so the
    name is the thing being asserted about and the model is one of its
    attributes. Naming the event after the model would make every model a
    separate vocabulary entry and nothing could assert over calls in
    general.

    `tags` carries only what a deterministic assertion can use -- the token
    counts the provider reported, and whether the reply parsed into the
    type that was asked for. It does NOT carry the prompt or the
    completion. A trace is kept, shipped and read by people who were not in
    the room, and the first layer of this instrument is the one that must
    be safe to keep.

    `position` is the shared ruler: it counts events and tool calls
    together, so `order` can assert that a model call came before a write.
    A recorder that only counts its own events would give `order` a ruler
    with one thing on it, which is not a ruler.
    """

    _events: list[Event] = field(default_factory=_no_events)
    _position: int = 0

    def _emit(self, name: str, tags: dict[str, object]) -> None:
        self._events.append(Event(self._position, name, tags))
        self._position += 1

    def model_call(self, model: str, *, output_type: str) -> None:
        """A request left for `model`, asking to be answered as a type."""
        self._emit("model_call", {"model": model, "output_type": output_type})

    def model_result(
        self,
        model: str,
        *,
        input_tokens: int,
        output_tokens: int,
        parsed: bool,
    ) -> None:
        """A reply arrived, and either did or did not parse."""
        self._emit(
            "model_result",
            {
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "parsed": parsed,
            },
        )

    @property
    def trace(self) -> Trace:
        """The events so far, frozen."""
        return Trace(events=tuple(self._events))
