import pytest

from exercises._loader import load
from trace_assert import ToolCall, Trace

RETRIED = Trace(
    tool_calls=(
        ToolCall(0, "list_leaves", attempts=1),
        ToolCall(1, "list_leaves", attempts=4),
    )
)


def attempts():  # type: ignore[no-untyped-def]
    return load("ch14", "e14_02_never_vacuous").call_attempts


def test_a_run_inside_the_bound_passes() -> None:
    attempts()(RETRIED, "list_leaves", 4)


def test_the_worst_call_decides_not_the_first() -> None:
    with pytest.raises(AssertionError) as failure:
        attempts()(RETRIED, "list_leaves", 3)
    assert "4" in str(failure.value)


def test_a_tool_never_called_fails_rather_than_passing() -> None:
    # The point of the exercise: max(nothing) is under every bound.
    with pytest.raises(AssertionError):
        attempts()(RETRIED, "request_time_off", 1)
    with pytest.raises(AssertionError):
        attempts()(Trace(), "list_leaves", 1)
