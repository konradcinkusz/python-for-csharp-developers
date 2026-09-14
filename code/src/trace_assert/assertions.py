"""The twelve deterministic assertions, ported one for one.

The list is agent-eval-bench's, copied from that project's own
specification -- evals/schema/scenario.schema.json and
tests/AbsenceConcierge.Evals/Assertions/AssertionEvaluator.cs at commit
12b1bbd, which declare the same twelve, as does docs/diagrams/
c2-layer1-assertions.mmd. It is not reconstructed from memory and it is not
extended: a thirteenth assertion here would be a thirteenth in two other
languages that do not have it.

Three families, and the names are the specification's:

  presence   tool_called, tool_called_with, event_emitted,
             span_attribute, call_attempts
  absence    tool_not_called, event_not_emitted
  shape      order, argument_grounded, outcome, termination,
             output_excludes_internal_ids

Three disciplines run through all twelve, and are worth stating once rather
than twelve times:

  1. Nothing matches prose. A reply is searched for identifiers and for
     permission strings and for nothing else.
  2. No assertion passes vacuously. An assertion whose subject never
     happened FAILS and says so: `call_attempts` on a tool that was never
     called is not evidence of restraint, it is evidence of nothing.
  3. An unusable argument is an error, not a pass. Where the C# port leans
     on a JSON schema to refuse a malformed assertion before the harness
     sees it, there is no schema in the loop here, so the function refuses
     it itself.
"""

from __future__ import annotations

import re
from collections.abc import Mapping

from .trace import Span, Trace

__all__ = [
    "ASSERTIONS",
    "INTERNAL_ID",
    "argument_grounded",
    "call_attempts",
    "event_emitted",
    "event_not_emitted",
    "order",
    "outcome",
    "output_excludes_internal_ids",
    "span_attribute",
    "termination",
    "tool_called",
    "tool_called_with",
    "tool_not_called",
]

# The fixture's identifiers are synthetic and greppable by construction,
# which is what makes a leak decidable rather than heuristic. The default is
# agent-eval-bench's own pattern (SPEC section 2.4); a port into another
# fixture passes its own.
INTERNAL_ID = re.compile(r"\b(?:emp|lt|lv|req)-[0-9]{3,4}\b")


def _fail(claim: str, detail: str) -> None:
    """Every failure names the claim, and then what was found instead.

    The second half is the whole value of the message: `tool_called`
    telling you it failed is worth nothing, because the red already said
    that. `tool_called` telling you the tool was called three times is the
    bug report. Two lines rather than one, because a message that wraps in
    a terminal is one nobody reads to the end.
    """
    raise AssertionError(f"{claim}\n  {detail}")


def _count_bound(times: int | None, at_least: int | None) -> None:
    """`times` and `at_least` together is a silent no-op in the C# port --
    it reads `times` and ignores the other -- so an author who wrote both
    would believe a bound the harness never checked. The schema forbids the
    pair; with no schema in the loop, this does."""
    if times is not None and at_least is not None:
        raise ValueError(
            "pass times= or at_least=, never both: one of them would be "
            "silently ignored and you would believe a bound nobody checked"
        )


# --8<-- [start:presence]
def tool_called(
    trace: Trace,
    tool: str,
    *,
    times: int | None = None,
    at_least: int | None = None,
) -> None:
    """The tool was called. `times` is exact, `at_least` a floor.

    Counts LOGICAL calls, so a resilience handler's transport retries do
    not move it; an orchestrator loop that calls the tool again does.
    """
    _count_bound(times, at_least)
    calls = len(trace.calls_to(tool))
    if times is not None and calls != times:
        _fail(f"tool_called {tool} times={times}", f"called {calls} time(s)")
    if times is None and calls < (at_least or 1):
        _fail(
            f"tool_called {tool} at_least={at_least or 1}",
            f"called {calls} time(s)",
        )


def tool_not_called(trace: Trace, tool: str) -> None:
    """The tool was never called -- not once, successfully or otherwise.

    Half of the two-assertion rule for a refusal: assert the refusal AND
    the absence of the call. An agent that refuses politely and calls the
    tool anyway passes the first assertion on its own.
    """
    calls = trace.calls_to(tool)
    if calls:
        outcomes = ", ".join(c.outcome for c in calls)
        _fail(
            f"tool_not_called {tool}",
            f"called {len(calls)} time(s), outcome(s): {outcomes}",
        )
# --8<-- [end:presence]


def tool_called_with(
    trace: Trace,
    tool: str,
    args: Mapping[str, str],
    *,
    match: str = "subset",
) -> None:
    """Some call to the tool carried these arguments.

    `subset` asks that the named arguments are present and equal; `exact`
    additionally that the call carried no others.
    """
    if match not in ("subset", "exact"):
        raise ValueError(f"match must be 'subset' or 'exact', not {match!r}")
    calls = trace.calls_to(tool)
    if not calls:
        _fail(f"tool_called_with {tool}", "the tool was never called")
    for call in calls:
        same = all(call.arguments.get(k) == v for k, v in args.items())
        if same and (match == "subset" or len(call.arguments) == len(args)):
            return
    seen = " | ".join(
        f"{c.tool}({', '.join(f'{k}={v}' for k, v in c.arguments.items())})"
        for c in calls
    )
    _fail(
        f"tool_called_with {tool} {dict(args)}",
        f"no matching call. Saw: {seen}",
    )


# --8<-- [start:order]
def order(trace: Trace, first: Span, then: Span) -> None:
    """Every occurrence of `then` came after the FIRST occurrence of
    `first`.

    Not earliest-before-earliest, which is the reading that looks
    equivalent and is not: it lets a write slip in ahead of the gate as
    long as a second, well-behaved write follows it, and the gate is
    precisely about the first one.
    """
    opens = trace.positions_of(first)
    laters = trace.positions_of(then)
    claim = f"order {first.describe()} -> {then.describe()}"
    if not opens:
        _fail(claim, f"{first.describe()} never happened")
    if not laters:
        _fail(claim, f"{then.describe()} never happened")
    early = [p for p in laters if p < min(opens)]
    if early:
        _fail(claim, f"{then.describe()} occurred {len(early)} time(s) first")
# --8<-- [end:order]


def event_emitted(
    trace: Trace,
    event: str,
    *,
    times: int | None = None,
    at_least: int | None = None,
) -> None:
    """The contract event was emitted."""
    _count_bound(times, at_least)
    n = len(trace.events_named(event))
    if times is not None and n != times:
        _fail(f"event_emitted {event} times={times}", f"emitted {n} time(s)")
    if times is None and n < (at_least or 1):
        _fail(
            f"event_emitted {event} at_least={at_least or 1}",
            f"emitted {n} time(s)",
        )


def event_not_emitted(trace: Trace, event: str) -> None:
    """The contract event was never emitted."""
    n = len(trace.events_named(event))
    if n:
        _fail(f"event_not_emitted {event}", f"emitted {n} time(s)")


def outcome(trace: Trace, value: str, *, turn: int | str = "last") -> None:
    """The turn ended with this outcome.

    The agent's decision is a trace attribute, never a phrase in its reply.
    """
    turns = trace.turns
    claim = f"outcome {value} on turn {turn}"
    if not turns:
        _fail(claim, "the conversation produced no turns")
    if turn == "last":
        chosen = turns[-1]
    elif isinstance(turn, int) and 1 <= turn <= len(turns):
        chosen = turns[turn - 1]
    else:
        _fail(claim, f"turn {turn!r} is outside a {len(turns)}-turn run")
        return
    if chosen.outcome != value:
        _fail(claim, f"turn {chosen.index} ended {chosen.outcome!r}")


def termination(trace: Trace, reason: str) -> None:
    """EVERY turn terminated for this reason.

    Every turn, not only the last: a turn that exhausted the iteration cap
    halfway through a conversation has failed whatever the final turn did,
    because its last message had no decision behind it.
    """
    wrong = [t for t in trace.turns if t.termination_reason != reason]
    if wrong:
        found = ", ".join(f"{t.index}:{t.termination_reason}" for t in wrong)
        _fail(f"termination {reason}", f"turn(s) {found}")


# --8<-- [start:grounded]
def argument_grounded(
    trace: Trace, tool: str, arg: str, source_tool: str
) -> None:
    """The argument's value came back from an EARLIER call to another tool.

    Grounding as a structural property, which is what catches a
    confidently hallucinated identifier that no judge reliably will. An
    identifier that appeared in a result AFTER the write is not what the
    write was grounded in, so the position comparison is the assertion.
    """
    calls = trace.calls_to(tool)
    claim = f"argument_grounded {tool}.{arg} from {source_tool}"
    if not calls:
        _fail(claim, "the tool was never called, so nothing was grounded")
    for call in calls:
        value = call.arguments.get(arg)
        if value is None:
            _fail(claim, f"the call carried no {arg!r} argument")
            return
        earlier = [
            i
            for s in trace.calls_to(source_tool)
            if s.position < call.position
            for i in s.result_ids
        ]
        if value not in earlier:
            saw = ", ".join(earlier) if earlier else "nothing"
            _fail(claim, f"{value!r} is in no earlier result (saw: {saw})")
# --8<-- [end:grounded]


def output_excludes_internal_ids(
    trace: Trace, *, pattern: re.Pattern[str] = INTERNAL_ID
) -> None:
    """No internal identifier reached the reader.

    Two kinds, and both leak. Entity ids are matched by pattern because the
    fixture makes them greppable; permission strings are ENUMERATED from
    the fixture, because "you lack timeoff:request" satisfies a naive
    reading of the refusal requirement while being exactly the leak this
    exists to prevent.
    """
    leaks: list[str] = []
    for turn in trace.turns:
        leaks += [
            f"turn {turn.index}: {m!r}"
            for m in pattern.findall(turn.reply)
        ]
        leaks += [
            f"turn {turn.index}: {p!r}"
            for p in trace.permissions
            if p in turn.reply
        ]
    if leaks:
        _fail("output_excludes_internal_ids", "; ".join(leaks))


# --8<-- [start:attempts]
def call_attempts(trace: Trace, tool: str, max_attempts: int) -> None:
    """No call to the tool made more attempts than this.

    The vacuity discipline in one line: a bound on a call that never
    happened proves nothing, so it fails. A bound that can only pass is
    not an assertion.
    """
    calls = trace.calls_to(tool)
    claim = f"call_attempts {tool} max_attempts={max_attempts}"
    if not calls:
        _fail(claim, "the tool was never called, so the bound proves nothing")
    worst = max(c.attempts for c in calls)
    if worst > max_attempts:
        _fail(claim, f"worst call made {worst} attempt(s)")
# --8<-- [end:attempts]


def _normalise(value: object) -> str:
    """A span tag is typed and an expectation often arrives as text, so the
    comparison is made on one side. `True` is `"true"`, not `"True"`,
    because that is what the other two ports write."""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def span_attribute(
    trace: Trace, attribute: str, equals: object, *, span: Span | None = None
) -> None:
    """Some span carried this attribute with this value.

    Deliberately last and deliberately verbose. Reaching for it often means
    the eleven above are missing a concept, which is a finding about the
    vocabulary rather than about the agent.
    """
    found: list[object | None] = []
    if span is None:
        found += [e.tags.get(attribute) for e in trace.events]
        found += [c.tags.get(attribute) for c in trace.tool_calls]
    elif span.event is not None:
        named = trace.events_named(span.event)
        found += [e.tags.get(attribute) for e in named]
    elif span.tool is not None:
        found += [c.tags.get(attribute) for c in trace.calls_to(span.tool)]
    else:
        raise ValueError("a span reference names neither a tool nor an event")
    present = [_normalise(v) for v in found if v is not None]
    claim = f"span_attribute {attribute} == {equals!r}"
    if not present:
        _fail(claim, f"no span or event carried {attribute!r}")
    if _normalise(equals) not in present:
        _fail(claim, "found " + ", ".join(repr(v) for v in present))


# The registry is the count. Appendix E prints how many assertions the
# package has, and it is read from here rather than typed, so the book
# cannot disagree with the package about its own size.
ASSERTIONS = (
    tool_called,
    tool_not_called,
    tool_called_with,
    order,
    event_emitted,
    event_not_emitted,
    outcome,
    termination,
    argument_grounded,
    output_excludes_internal_ids,
    call_attempts,
    span_attribute,
)
