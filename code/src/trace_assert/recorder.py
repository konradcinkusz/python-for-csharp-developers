"""The mutable half: what a run writes into while it is running.

The split that matters is Recorder against Trace. A Recorder belongs to the
RUN -- the code under test appends to it while it works -- and a Trace
belongs to the ASSERTIONS: it is the evidence, and an assertion that could
edit the evidence is not an assertion. That is why `trace` builds a new
immutable snapshot rather than handing out the recorder's own lists.

Two stages meet here. Chapter 11 records tool calls, which is what the
presence assertions count; chapter 13 records a model call, which is the
join between a real SDK and this instrument. Both write onto one shared
`position` ruler, and that is the whole reason the two halves live in one
object: `order` compares a tool call against an event, and two recorders
counting separately would give it two rulers and no way to interleave them.

A model call is TWO events and not one. A call that never came back is the
case most worth being able to find, and a single event written after the
reply cannot represent it -- there is nothing to write when nothing
arrives.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .trace import Event, ToolCall, Trace, as_text

__all__ = ["Recorder"]


def _no_events() -> list[Event]:
    """A typed empty list, for the reason `_no_tags` is a typed empty dict:
    `default_factory=list` is list[Unknown] to a strict checker, which is
    chapter 3's lesson arriving in the package the whole book builds."""
    return []


def _no_calls() -> list[ToolCall]:
    return []


@dataclass(slots=True)
class Recorder:
    """Collects a run in order, and hands back a Trace nothing can edit.

    The event's `name` is the KIND -- `model_call`, `model_result` -- and
    the model is a tag. That is the way round the assertions read: they ask
    `events_named("model_call")` and `Span.of_event("model_call")`, so the
    name is the thing being asserted about and the model is one of its
    attributes. Naming the event after the model would make every model a
    separate vocabulary entry and nothing could assert over calls in
    general.

    What is written down is only what a deterministic assertion can use --
    a call's arguments, the token counts the provider reported, whether the
    reply parsed into the type that was asked for. It does NOT carry the
    prompt or the completion. A trace is kept, shipped and read by people
    who were not in the room, and the first layer of this instrument is the
    one that must be safe to keep.
    """

    _calls: list[ToolCall] = field(default_factory=_no_calls)
    _events: list[Event] = field(default_factory=_no_events)
    _position: int = 0

    def _next(self) -> int:
        """The shared ruler. Tool calls and events are numbered together."""
        position = self._position
        self._position += 1
        return position

    def tool_call(
        self,
        tool: str,
        *,
        kind: str = "read",
        outcome: str = "success",
        attempts: int = 1,
        result_ids: tuple[str, ...] = (),
        **arguments: object,
    ) -> None:
        """One LOGICAL tool call: the call and how it ended, together.

        A result is not a separate record. A call exists whether it
        succeeded or not, so folding the outcome into the call is what
        keeps "the write was never attempted" and "the write failed" from
        looking alike in the evidence -- and `tool_not_called` quotes the
        outcome of every call it found for exactly that reason.

        Everything not named above is an ARGUMENT of the call, stringified
        through the package's one stringifier so that what the recorder
        writes and what `tool_called_with` reads cannot disagree. A tool
        whose own parameter is called `kind` or `outcome` therefore has to
        be recorded by building the ToolCall directly; the original's
        schema keeps arguments in their own object for the same reason.
        """
        self._calls.append(
            ToolCall(
                position=self._next(),
                tool=tool,
                kind=kind,
                outcome=outcome,
                arguments={k: as_text(v) for k, v in arguments.items()},
                result_ids=result_ids,
                attempts=attempts,
            )
        )

    def _emit(self, name: str, tags: dict[str, object]) -> None:
        self._events.append(Event(self._next(), name, tags))

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
        """Everything recorded so far, frozen."""
        return Trace(
            tool_calls=tuple(self._calls), events=tuple(self._events)
        )
