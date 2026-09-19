"""Exercise 14.1 -- port one assertion.

`tool_called_with` asks whether SOME call to a tool carried the arguments
you named. Two readings of "carried", and the caller picks:

    subset   the named arguments are present and equal, others allowed
    exact    the named arguments are present and equal, and there are
             no others

Write it. The test beside this file checks both readings, and it also
checks the case that separates a real assertion from a vacuous one: a tool
that was never called must FAIL, not pass for want of a counterexample.

Raise AssertionError on failure -- that is what a pytest assertion is --
and put in the message what you found instead of what was asked for.
"""

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
    raise NotImplementedError("your turn: replace this line")
