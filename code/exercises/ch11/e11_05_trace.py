"""Exercise 11.5 -- the guiding project's first two assertions, used.

A refund agent may pay out by itself up to a limit, and above it must ask a
human instead. Implement `handle_refund` so that it records what it did on
the recorder it is given:

  * always record a `check_policy` tool call, first;
  * at or below LIMIT_PENCE, record a `pay_refund` tool call;
  * above it, record a `request_approval` tool call and NOT `pay_refund`.

Record a tool call with `recorder.tool_call(name)`. The test asserts both
halves with trace-assert: the call that should have happened, and the one
that must not have. An agent that refuses in prose and pays out anyway
passes the first half on its own, which is why there are two.
"""

from trace_assert import Recorder

LIMIT_PENCE = 5000


def handle_refund(recorder: Recorder, pence: int) -> str:
    """Record the calls, and return "paid" or "escalated"."""
    raise NotImplementedError("your turn: replace this line")
