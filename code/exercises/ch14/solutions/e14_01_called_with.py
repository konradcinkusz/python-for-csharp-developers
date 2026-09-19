"""Reference solution for exercise 14.1."""

from __future__ import annotations

from collections.abc import Mapping

from trace_assert import Trace


def tool_called_with(
    trace: Trace,
    tool: str,
    args: Mapping[str, str],
    *,
    match: str = "subset",
) -> None:
    """Assert that some call to `tool` carried `args`."""
    if match not in ("subset", "exact"):
        raise ValueError(f"match must be 'subset' or 'exact', not {match!r}")
    calls = trace.calls_to(tool)
    if not calls:
        # Never a silent pass: an argument claim about a call that did not
        # happen is a claim with nothing behind it.
        raise AssertionError(
            f"tool_called_with {tool}\n  the tool was never called"
        )
    for call in calls:
        same = all(call.arguments.get(k) == v for k, v in args.items())
        if same and (match == "subset" or len(call.arguments) == len(args)):
            return
    seen = " | ".join(str(dict(c.arguments)) for c in calls)
    raise AssertionError(
        f"tool_called_with {tool} {dict(args)}\n  no matching call: {seen}"
    )
