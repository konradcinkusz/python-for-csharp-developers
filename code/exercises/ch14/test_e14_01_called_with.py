import pytest

from exercises._loader import load
from trace_assert import ToolCall, Trace

TRACE = Trace(
    tool_calls=(
        ToolCall(0, "list_leaves"),
        ToolCall(
            1,
            "request_time_off",
            kind="write",
            arguments={"leave_type_id": "lt-0012", "days": "3"},
        ),
    )
)


def called_with():  # type: ignore[no-untyped-def]
    return load("ch14", "e14_01_called_with").tool_called_with


def test_subset_matches_a_call_that_carried_more() -> None:
    called_with()(TRACE, "request_time_off", {"days": "3"})


def test_exact_refuses_a_call_that_carried_more() -> None:
    with pytest.raises(AssertionError):
        called_with()(
            TRACE, "request_time_off", {"days": "3"}, match="exact"
        )
    called_with()(
        TRACE,
        "request_time_off",
        {"days": "3", "leave_type_id": "lt-0012"},
        match="exact",
    )


def test_a_wrong_value_fails_and_the_message_names_what_was_found() -> None:
    with pytest.raises(AssertionError) as failure:
        called_with()(TRACE, "request_time_off", {"days": "9"})
    assert "3" in str(failure.value)


def test_a_tool_never_called_fails_rather_than_passing() -> None:
    with pytest.raises(AssertionError):
        called_with()(Trace(), "request_time_off", {"days": "3"})
