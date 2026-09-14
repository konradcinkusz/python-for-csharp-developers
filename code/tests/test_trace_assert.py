"""The guiding project's own suite.

Every assertion is watched producing a known answer in BOTH directions: a
trace it must accept and a trace it must reject. A check that has only ever
been seen passing is a check nobody has evidence for, and `call_attempts` is
the one in this set that would otherwise pass on a run where the tool was
never called at all.
"""

from __future__ import annotations

import re

import pytest

from trace_assert import (
    ASSERTIONS,
    Event,
    Span,
    ToolCall,
    Trace,
    Turn,
    __version__,
    argument_grounded,
    call_attempts,
    event_emitted,
    event_not_emitted,
    order,
    outcome,
    output_excludes_internal_ids,
    span_attribute,
    termination,
    tool_called,
    tool_called_with,
    tool_not_called,
)

# One well-behaved run: look the types up, check the diary, show a draft,
# take the approval, and only then write. The identifier in the write came
# back from the earlier read, which is what makes the write grounded.
GOOD = Trace(
    tool_calls=(
        ToolCall(0, "list_leave_types", result_ids=("lt-0012",)),
        ToolCall(1, "list_leaves"),
        ToolCall(
            4,
            "request_time_off",
            kind="write",
            arguments={"leave_type_id": "lt-0012", "days": "3"},
            tags={"workforce.tool.days": 3},
        ),
    ),
    events=(
        Event(2, "confirmation.shown", {"confirmation.working_days": 3}),
        Event(3, "confirmation.received"),
    ),
    turns=(
        Turn(1, "confirmation_pending", reply="Three days, 9 to 11 March?"),
        Turn(2, "completed", reply="Booked: 9 to 11 March."),
    ),
    permissions=("timeoff:read", "timeoff:request"),
)

# The same run with the gate jumped: the write happens before the approval.
UNGATED = Trace(
    tool_calls=(ToolCall(0, "request_time_off", kind="write"),),
    events=(Event(1, "confirmation.received"),),
    turns=(Turn(1, "completed", reply="Booked."),),
)


def test_the_package_knows_its_own_size() -> None:
    # The count Appendix E prints is read from here, not typed.
    assert len(ASSERTIONS) == 12
    assert len({f.__name__ for f in ASSERTIONS}) == 12
    assert isinstance(__version__, str)


def test_evidence_is_immutable() -> None:
    with pytest.raises(AttributeError):
        GOOD.turns[0].outcome = "refused"  # type: ignore[misc]


# --8<-- [start:presence]
def test_presence_and_absence() -> None:
    tool_called(GOOD, "list_leave_types")
    tool_called(GOOD, "request_time_off", times=1)
    tool_not_called(GOOD, "delete_everything")
    with pytest.raises(AssertionError, match="called 1 time"):
        tool_called(GOOD, "request_time_off", times=2)
    with pytest.raises(AssertionError, match="outcome"):
        tool_not_called(GOOD, "request_time_off")


def test_a_count_bound_must_be_one_or_the_other() -> None:
    # Both together is the shape that makes an author believe a bound
    # nobody checked. The C# port silently prefers `times`; this refuses.
    with pytest.raises(ValueError, match="never both"):
        tool_called(GOOD, "list_leaves", times=1, at_least=1)
# --8<-- [end:presence]


def test_arguments() -> None:
    tool_called_with(GOOD, "request_time_off", {"leave_type_id": "lt-0012"})
    tool_called_with(
        GOOD,
        "request_time_off",
        {"leave_type_id": "lt-0012", "days": "3"},
        match="exact",
    )
    with pytest.raises(AssertionError, match="no matching call"):
        tool_called_with(GOOD, "request_time_off", {"days": "9"})
    with pytest.raises(AssertionError, match="no matching call"):
        # Right values, but the call carried a second argument as well.
        tool_called_with(
            GOOD, "request_time_off", {"days": "3"}, match="exact"
        )
    with pytest.raises(AssertionError, match="never called"):
        tool_called_with(UNGATED, "list_leaves", {"a": "b"})
    with pytest.raises(ValueError, match="subset"):
        tool_called_with(GOOD, "list_leaves", {"a": "b"}, match="loose")


# --8<-- [start:order]
def test_order_is_about_the_first_occurrence() -> None:
    gate = Span.of_event("confirmation.received")
    write = Span.of_tool("request_time_off")
    order(GOOD, first=gate, then=write)
    with pytest.raises(AssertionError, match="occurred 1 time"):
        order(UNGATED, first=gate, then=write)


def test_order_fails_when_either_side_never_happened() -> None:
    # Not a pass. An ordering between two things, one of which did not
    # occur, is a claim with nothing behind it.
    with pytest.raises(AssertionError, match="never happened"):
        order(
            GOOD,
            first=Span.of_event("refusal.issued"),
            then=Span.of_tool("request_time_off"),
        )
# --8<-- [end:order]


def test_events() -> None:
    event_emitted(GOOD, "confirmation.shown", times=1)
    event_emitted(GOOD, "confirmation.received", at_least=1)
    event_not_emitted(GOOD, "refusal.issued")
    with pytest.raises(AssertionError, match="emitted 0 time"):
        event_emitted(GOOD, "refusal.issued")
    with pytest.raises(AssertionError, match="emitted 1 time"):
        event_not_emitted(GOOD, "confirmation.shown")


def test_outcome_names_a_turn() -> None:
    outcome(GOOD, "completed")
    outcome(GOOD, "confirmation_pending", turn=1)
    with pytest.raises(AssertionError, match="ended 'completed'"):
        outcome(GOOD, "refused")
    with pytest.raises(AssertionError, match="outside a 2-turn run"):
        outcome(GOOD, "completed", turn=9)
    with pytest.raises(AssertionError, match="no turns"):
        outcome(Trace(), "completed")


def test_termination_is_about_every_turn() -> None:
    termination(GOOD, "decision")
    mid_cap = Trace(
        turns=(
            Turn(1, "completed", termination_reason="iteration_cap"),
            Turn(2, "completed", termination_reason="decision"),
        )
    )
    with pytest.raises(AssertionError, match="1:iteration_cap"):
        termination(mid_cap, "decision")


# --8<-- [start:grounded]
def test_grounding_is_structural_and_looks_backwards() -> None:
    argument_grounded(GOOD, "request_time_off", "leave_type_id",
                      "list_leave_types")
    # The same identifier, returned by a read that happened AFTER the
    # write. The write cannot have been grounded in it.
    late = Trace(
        tool_calls=(
            ToolCall(0, "request_time_off", kind="write",
                     arguments={"leave_type_id": "lt-0012"}),
            ToolCall(1, "list_leave_types", result_ids=("lt-0012",)),
        )
    )
    with pytest.raises(AssertionError, match="no earlier result"):
        argument_grounded(late, "request_time_off", "leave_type_id",
                          "list_leave_types")
# --8<-- [end:grounded]


def test_grounding_fails_when_nothing_was_called_or_carried() -> None:
    with pytest.raises(AssertionError, match="never called"):
        argument_grounded(Trace(), "request_time_off", "x", "y")
    bare = Trace(tool_calls=(ToolCall(0, "request_time_off", kind="write"),))
    with pytest.raises(AssertionError, match="carried no 'x'"):
        argument_grounded(bare, "request_time_off", "x", "y")


def test_identifiers_and_permissions_both_leak() -> None:
    output_excludes_internal_ids(GOOD)
    leaked_id = Trace(turns=(Turn(1, "completed", reply="Booked lv-0041."),))
    with pytest.raises(AssertionError, match="lv-0041"):
        output_excludes_internal_ids(leaked_id)
    # The one a pattern would miss, and the one a naive refusal produces.
    leaked_perm = Trace(
        turns=(Turn(1, "refused", reply="You lack timeoff:request."),),
        permissions=("timeoff:request",),
    )
    with pytest.raises(AssertionError, match="timeoff:request"):
        output_excludes_internal_ids(leaked_perm)


def test_a_caller_can_bring_its_own_identifier_pattern() -> None:
    other = Trace(turns=(Turn(1, "completed", reply="see acct-77"),))
    output_excludes_internal_ids(other)
    with pytest.raises(AssertionError, match="acct-77"):
        output_excludes_internal_ids(
            other, pattern=re.compile(r"\bacct-[0-9]{2}\b")
        )


# --8<-- [start:attempts]
def test_an_attempt_bound_never_passes_vacuously() -> None:
    call_attempts(GOOD, "request_time_off", 1)
    # The tool was never called. The bound is satisfied by a run in which
    # nothing happened, so it fails rather than reporting restraint.
    with pytest.raises(AssertionError, match="proves nothing"):
        call_attempts(GOOD, "find_employee", 3)
# --8<-- [end:attempts]


def test_attempts_counts_the_worst_call() -> None:
    retried = Trace(
        tool_calls=(
            ToolCall(0, "list_leaves", attempts=1),
            ToolCall(1, "list_leaves", attempts=4),
        )
    )
    with pytest.raises(AssertionError, match="worst call made 4"):
        call_attempts(retried, "list_leaves", 3)


def test_span_attribute_is_the_escape_hatch() -> None:
    span_attribute(GOOD, "confirmation.working_days", 3)
    span_attribute(
        GOOD,
        "workforce.tool.days",
        "3",
        span=Span.of_tool("request_time_off"),
    )
    with pytest.raises(AssertionError, match="no span or event carried"):
        span_attribute(GOOD, "confirmation.excluded_days", 1)
    with pytest.raises(AssertionError, match="found '3'"):
        span_attribute(GOOD, "confirmation.working_days", 5)


def test_a_boolean_tag_normalises_the_way_the_other_ports_write_it() -> None:
    flagged = Trace(events=(Event(0, "confirmation.shown",
                                  {"attachment_required": True}),))
    span_attribute(flagged, "attachment_required", "true")
    span_attribute(flagged, "attachment_required", True)
