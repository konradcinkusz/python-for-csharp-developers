from trace_assert import Event, Trace, __version__


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
