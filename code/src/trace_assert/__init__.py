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

__all__ = ["Event", "Trace", "__version__"]

__version__ = "0.0.1"


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
