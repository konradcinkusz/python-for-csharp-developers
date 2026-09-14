"""Exercise 11.5: assert the refusal AND that the call never happened."""

from exercises._loader import load
from trace_assert import Recorder, assert_tool_called, assert_tool_not_called

KEY = "e11_05_trace"


def test_a_small_refund_is_paid(trace: Recorder) -> None:
    module = load("ch11", KEY)
    assert module.handle_refund(trace, 100) == "paid"
    assert_tool_called(trace.trace, "check_policy", times=1)
    assert_tool_called(trace.trace, "pay_refund", times=1)
    assert_tool_not_called(trace.trace, "request_approval")


def test_the_limit_itself_is_still_paid(trace: Recorder) -> None:
    module = load("ch11", KEY)
    assert module.handle_refund(trace, module.LIMIT_PENCE) == "paid"
    assert_tool_called(trace.trace, "pay_refund", times=1)


def test_a_large_refund_is_escalated_and_not_paid(trace: Recorder) -> None:
    module = load("ch11", KEY)
    assert module.handle_refund(trace, 999_999) == "escalated"
    assert_tool_called(trace.trace, "request_approval", times=1)
    # The half that is easy to leave out, and the only one that catches an
    # agent which says no and pays out anyway.
    assert_tool_not_called(trace.trace, "pay_refund")


def test_the_policy_is_always_checked_first(trace: Recorder) -> None:
    module = load("ch11", KEY)
    module.handle_refund(trace, 999_999)
    assert trace.trace.names("tool_call")[0] == "check_policy"
