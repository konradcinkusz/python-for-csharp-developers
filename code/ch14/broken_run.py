"""The same suite over a run that went wrong, printing what it says.

Run it from code/:   uv run python ch14/broken_run.py

A failure message that says only which assertion failed is worth nothing:
you already knew that from the red. The message has to name what was found
instead, because that is the bug report. Every one of the twelve carries
its own, and this file exists to print four of them side by side.

The run below is the classic agent defect: the write happens before the
approval, the identifier in it came from nowhere, the reply leaks the
identifier to the user, and the turn ended by exhausting its iteration cap
rather than by deciding anything.
"""

from __future__ import annotations

import sys
from collections.abc import Callable

from trace_assert import (
    Event,
    Span,
    ToolCall,
    Trace,
    Turn,
    argument_grounded,
    order,
    output_excludes_internal_ids,
    termination,
)

# --8<-- [start:broken]
BROKEN = Trace(
    tool_calls=(
        ToolCall(
            0,
            "request_time_off",
            kind="write",
            arguments={"leave_type_id": "lt-0099"},
        ),
    ),
    events=(Event(1, "confirmation.received"),),
    turns=(
        Turn(
            1,
            "completed",
            termination_reason="iteration_cap",
            reply="Booked lv-0041 for you.",
        ),
    ),
)


CHECKS: tuple[Callable[[], None], ...] = (
    lambda: order(
        BROKEN,
        first=Span.of_event("confirmation.received"),
        then=Span.of_tool("request_time_off"),
    ),
    lambda: argument_grounded(
        BROKEN, "request_time_off", "leave_type_id", "list_leave_types"
    ),
    lambda: output_excludes_internal_ids(BROKEN),
    lambda: termination(BROKEN, "decision"),
)
# --8<-- [end:broken]


def main() -> int:
    for check in CHECKS:
        try:
            check()
        except AssertionError as failure:
            print(failure)
        else:  # pragma: no cover - the run above is broken on purpose
            print("PASSED, which this file exists to prevent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
