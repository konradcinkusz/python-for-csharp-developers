"""Reference solution for exercise 11.5."""

from trace_assert import Recorder

LIMIT_PENCE = 5000


def handle_refund(recorder: Recorder, pence: int) -> str:
    """Record the calls, and return "paid" or "escalated"."""
    recorder.tool_call("check_policy", pence=pence)
    if pence <= LIMIT_PENCE:
        recorder.tool_call("pay_refund", pence=pence, outcome="ok")
        return "paid"
    recorder.tool_call("request_approval", pence=pence, outcome="ok")
    return "escalated"
