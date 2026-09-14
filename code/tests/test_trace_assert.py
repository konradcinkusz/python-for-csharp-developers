"""The guiding project's own suite. No network, no database, no model.

The scaffold's three tests covered the model. Stage 01 adds the Recorder,
the `trace` fixture and the two assertions -- and, for each assertion, a
test of what it says when it FAILS. An assertion whose failure message is
untested is a message nobody has read, and the message is the whole product:
a reader looking at a red suite gets the message and not the source.
"""

import pytest

from trace_assert import (
    Event,
    Recorder,
    Trace,
    __version__,
    assert_tool_called,
    assert_tool_not_called,
)


def test_trace_is_ordered_and_filterable() -> None:
    trace = Trace(
        (
            Event("model_call", "claude"),
            Event("tool_call", "search", {"q": "uv lockfile"}),
            Event("tool_result", "search"),
            Event("tool_call", "read_file", {"path": "pyproject.toml"}),
        )
    )
    assert trace.names("tool_call") == ("search", "read_file")
    assert trace.of_kind("model_call")[0].name == "claude"


def test_events_are_immutable() -> None:
    event = Event("tool_call", "search")
    try:
        event.name = "other"  # type: ignore[misc]
    except AttributeError:
        return
    raise AssertionError("an Event must not be mutable: it is evidence")


def test_version_is_a_string() -> None:
    assert isinstance(__version__, str)


# --------------------------------------------------------------------
# The Recorder: mutable while the run happens, immutable once asserted on.
# --------------------------------------------------------------------

def test_recorder_snapshot_does_not_change_underneath_an_assertion(
    trace: Recorder,
) -> None:
    trace.tool_call("search")
    snapshot = trace.trace
    trace.tool_call("write_leave")
    # The snapshot taken before the second call still shows one call: an
    # assertion holding a Trace is holding evidence, not a live view.
    assert snapshot.names("tool_call") == ("search",)
    assert trace.trace.names("tool_call") == ("search", "write_leave")


def test_the_trace_fixture_is_a_fresh_recorder(trace: Recorder) -> None:
    # Function scope, asserted rather than assumed: were it any wider, the
    # count assertions below would be counting the previous test's calls.
    assert trace.trace.events == ()


# --------------------------------------------------------------------
# assert_tool_called
# --------------------------------------------------------------------

def test_tool_called_passes_on_presence(trace: Recorder) -> None:
    trace.tool_call("search")
    assert_tool_called(trace.trace, "search")


def test_tool_called_counts_exactly(trace: Recorder) -> None:
    trace.tool_call("search")
    trace.tool_call("search")
    assert_tool_called(trace.trace, "search", times=2)
    assert_tool_called(trace.trace, "search", at_least=1)


def test_tool_called_names_what_it_saw_instead(trace: Recorder) -> None:
    trace.tool_call("read_leave")
    with pytest.raises(AssertionError) as caught:
        assert_tool_called(trace.trace, "write_leave")
    message = str(caught.value)
    assert "'write_leave'" in message
    assert "called 0 time(s)" in message
    # The point of the message: it names the call that DID happen.
    assert "read_leave" in message


def test_tool_called_reports_the_count_it_found(trace: Recorder) -> None:
    trace.tool_call("search")
    with pytest.raises(AssertionError, match=r"called 1 time\(s\)"):
        assert_tool_called(trace.trace, "search", times=3)


def test_tool_called_refuses_both_bounds(trace: Recorder) -> None:
    # Not an AssertionError: the test itself is malformed, and resolving it
    # silently is how a bound nobody checks gets believed.
    with pytest.raises(ValueError, match="not both"):
        assert_tool_called(trace.trace, "search", times=1, at_least=1)


# --------------------------------------------------------------------
# assert_tool_not_called
# --------------------------------------------------------------------

def test_tool_not_called_passes_on_absence(trace: Recorder) -> None:
    trace.tool_call("search")
    assert_tool_not_called(trace.trace, "write_leave")


def test_tool_not_called_distinguishes_failed_from_never_attempted(
    trace: Recorder,
) -> None:
    trace.tool_call("write_leave", outcome="error")
    with pytest.raises(AssertionError) as caught:
        assert_tool_not_called(trace.trace, "write_leave")
    # A tool that was called and failed is not a tool that was never
    # called, and the message has to say which one happened.
    assert "outcome(s): error" in str(caught.value)


def test_tool_not_called_says_so_when_no_outcome_was_recorded(
    trace: Recorder,
) -> None:
    trace.tool_call("write_leave")
    with pytest.raises(AssertionError, match="outcome\\(s\\): unrecorded"):
        assert_tool_not_called(trace.trace, "write_leave")
