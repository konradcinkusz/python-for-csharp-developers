"""The trace: the whole interface a deterministic assertion grades.

Ported from agent-eval-bench's `TraceRecording`
(tests/AbsenceConcierge.Evals/Execution/TraceRecording.cs, commit 12b1bbd),
which is also what the TypeScript port's `traceSchema` is built from. Three
languages, one shape: that is the only reason a comparison between the ports
means anything.

A trace is NOT a flat log of events. It is three parallel records -- tool
calls, contract events and turns -- and the first two share one `position`
index, because `order` has to compare a tool call against an event on the
same ruler. A single list with a `kind` discriminator cannot do that without
inventing the ruler afterwards, and the ruler is the whole of what `order`
asserts over.

What is deliberately NOT here is anything that would let an assertion match
the agent's prose, except `Turn.reply`, which exists solely so that
`output_excludes_internal_ids` can search it for identifiers. The moment an
assertion matches text like "I've booked", every rewording of a prompt
becomes a false regression, and the suite starts grading phrasing rather
than behaviour.
"""

from __future__ import annotations

from dataclasses import dataclass, field

__all__ = ["Event", "Span", "ToolCall", "Trace", "Turn", "as_text"]


def _no_arguments() -> dict[str, str]:
    """A typed empty dict. `default_factory=dict` is dict[Unknown, Unknown]
    to a strict checker, which is Chapter 3's lesson arriving in the one
    package the whole book builds."""
    return {}


def _no_tags() -> dict[str, object]:
    return {}


def as_text(value: object) -> str:
    """One stringifier for the whole package.

    A recorded argument arrives typed and an expectation is usually
    written as text, so the comparison has to be made on one side of
    the pair. It lives here rather than in `assertions` because BOTH
    halves need it -- the recorder writing a call's arguments and the
    assertions reading them -- and two copies of a rule about equality
    is how a recorder and its own assertions come to disagree.

    `True` is `"true"` and not `"True"`, because that is what the
    other two ports write.
    """
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


# --8<-- [start:model]
@dataclass(frozen=True, slots=True)
class ToolCall:
    """One LOGICAL tool call, however many transport attempts it took.

    A retry performed by a resilience handler underneath the agent is an
    attempt inside this call, counted in `attempts`; an orchestrator that
    calls the tool again opens a second `ToolCall`. The two are different
    numbers answering different questions, and conflating them is how a
    double submission hides.

    A call exists whether it succeeded or not: "the write was never
    attempted" and "the write failed" must not look alike in the evidence.
    """

    position: int
    tool: str
    kind: str = "read"
    outcome: str = "success"
    arguments: dict[str, str] = field(default_factory=_no_arguments)
    result_ids: tuple[str, ...] = ()
    attempts: int = 1
    tags: dict[str, object] = field(default_factory=_no_tags)


@dataclass(frozen=True, slots=True)
class Event:
    """One contract event, on the same ruler as the tool calls."""

    position: int
    name: str
    tags: dict[str, object] = field(default_factory=_no_tags)


@dataclass(frozen=True, slots=True)
class Turn:
    """One turn's graded result. `index` is 1-based, so that a scenario can
    name a turn the way a reader counts them."""

    index: int
    outcome: str
    termination_reason: str = "decision"
    reply: str = ""
# --8<-- [end:model]


@dataclass(frozen=True, slots=True)
class Span:
    """A reference to one tool call or one event, by name.

    Exactly one of the two, which the constructors enforce: a reference
    naming both is a question with two subjects, and the C# original throws
    on it rather than picking one.
    """

    tool: str | None = None
    event: str | None = None

    @staticmethod
    def of_tool(name: str) -> Span:
        return Span(tool=name)

    @staticmethod
    def of_event(name: str) -> Span:
        return Span(event=name)

    def describe(self) -> str:
        """Short on purpose: it goes inside a failure message, and a
        failure message that wraps in a terminal is one nobody reads."""
        if self.tool is not None:
            return f"tool:{self.tool}"
        if self.event is not None:
            return f"event:{self.event}"
        return "a span naming neither a tool nor an event"


@dataclass(frozen=True, slots=True)
class Trace:
    """The recorded run, in the shape the assertions are written against.

    Tuples rather than lists throughout, so that an assertion cannot mutate
    the evidence it is asserting over.

    `permissions` is the vocabulary of permission strings present in the
    scenario's fixture. It is enumerated rather than pattern-matched: a
    regular expression like `^[a-z]+:[a-z]+$` flags ordinary prose, and a
    rule that fires on prose is a rule somebody switches off.
    """

    tool_calls: tuple[ToolCall, ...] = ()
    events: tuple[Event, ...] = ()
    turns: tuple[Turn, ...] = ()
    permissions: tuple[str, ...] = ()

    def calls_to(self, tool: str) -> tuple[ToolCall, ...]:
        """Every call to one tool, in the order they were made."""
        return tuple(c for c in self.tool_calls if c.tool == tool)

    def events_named(self, name: str) -> tuple[Event, ...]:
        """Every event of one name, in the order they were emitted."""
        return tuple(e for e in self.events if e.name == name)

    def positions_of(self, span: Span) -> tuple[int, ...]:
        """Where a span happened, on the one shared ruler."""
        if span.tool is not None:
            return tuple(c.position for c in self.calls_to(span.tool))
        if span.event is not None:
            return tuple(e.position for e in self.events_named(span.event))
        raise ValueError("a span reference names neither a tool nor an event")
