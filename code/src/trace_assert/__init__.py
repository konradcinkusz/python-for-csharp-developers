"""trace-assert: deterministic assertions over an agent's execution trace.

This is the guiding project of *Python for .NET Engineers*. It is a port to
Python of the first layer of agent-eval-bench: the questions a test can
answer about an agent's run with no model, no budget and no judgement.
*Did it call the tool it was supposed to? In the order it was supposed to?
With arguments that came from somewhere? Without calling anything it was
forbidden?*

The trace model and the twelve assertions are that project's own, copied
from its specification at commit 12b1bbd and not reconstructed: the point
of the exercise is that three languages implement one design, and a
thirteenth assertion invented here would be a thirteenth in two other
languages that do not have it.

Every name below is a claim about the finished package. Usage:

    from trace_assert import Trace, ToolCall, tool_called, tool_not_called

    def test_the_gate_held(trace: Trace) -> None:
        tool_called(trace, "list_leave_types")
        tool_not_called(trace, "request_time_off")
"""

from __future__ import annotations

from .assertions import (
    ASSERTIONS,
    INTERNAL_ID,
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
from .trace import Event, Span, ToolCall, Trace, Turn

__all__ = [
    "ASSERTIONS",
    "INTERNAL_ID",
    "Event",
    "Span",
    "ToolCall",
    "Trace",
    "Turn",
    "__version__",
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

__version__ = "0.1.0"
