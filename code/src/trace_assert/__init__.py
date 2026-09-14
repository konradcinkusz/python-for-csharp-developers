"""trace-assert: deterministic assertions over an agent's execution trace.

This is the guiding project of *Python for .NET Engineers*. It is a port to
Python of the first layer of agent-eval-bench, and it is built up one stage
per chapter: the trace model and the first two assertions in chapter 11,
trace capture from a real model call in chapter 13, the full assertion set
and packaging in chapter 14.

What is here now is the model and nothing else, so that the package exists
from the first commit and the book's build has been running it since. Every
public name is a claim about the finished package, so the surface is kept as
small as the chapters have earned.
"""

from __future__ import annotations

from dataclasses import dataclass, field

__all__ = ["Event", "Recorder", "Trace", "__version__"]

__version__ = "0.0.2"


def _no_events() -> list[Event]:
    """A typed empty list, for the same reason `_empty_payload` is a
    typed empty dict: `default_factory=list` is list[Unknown]."""
    return []


def _empty_payload() -> dict[str, object]:
    """A typed empty dict: `default_factory=dict` is dict[Unknown, Unknown]
    to a strict checker, and that is the chapter 3 lesson arriving early."""
    return {}


@dataclass(frozen=True, slots=True)
class Event:
    """One thing the agent did, in the order it did it.

    `kind` is what happened -- `tool_call`, `tool_result`, `model_call`,
    `model_result` -- and `name` is what it happened to. Everything else is
    in `payload`, which stays untyped: a payload is evidence, and evidence
    from two different sources does not have one shape. What a MODEL call
    puts in it is settled by `Recorder` below, in chapter 13.
    """

    kind: str
    name: str
    payload: dict[str, object] = field(default_factory=_empty_payload)


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


@dataclass(slots=True)
class Recorder:
    """Collects events in order, and hands back a Trace nothing can edit.

    Stage 02, chapter 13. The trace model above says what an event is; this
    says what a MODEL call contributes to one, which the skeleton
    deliberately left open. Two events, not one: a call that never came
    back is the case worth being able to assert on, and a single event
    written after the reply cannot represent it.

    The payload carries only what a deterministic assertion can use -- the
    token counts the provider reported, and whether the reply parsed into
    the type that was asked for. It does NOT carry the prompt or the
    completion. A trace is kept, shipped and read by people who were not in
    the room, and the first layer of this instrument is the one that must
    be safe to keep.
    """

    _events: list[Event] = field(default_factory=_no_events)

    def model_call(self, model: str, *, output_type: str) -> None:
        """A request left for `model`, asking to be answered as a type."""
        self._events.append(
            Event("model_call", model, {"output_type": output_type})
        )

    def model_result(
        self,
        model: str,
        *,
        input_tokens: int,
        output_tokens: int,
        parsed: bool,
    ) -> None:
        """A reply arrived, and either did or did not parse."""
        self._events.append(
            Event(
                "model_result",
                model,
                {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "parsed": parsed,
                },
            )
        )

    @property
    def trace(self) -> Trace:
        """The events so far, frozen."""
        return Trace(tuple(self._events))
