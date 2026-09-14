from exercises._loader import load
from trace_assert import Recorder, Trace


def _recorded() -> Trace:
    recorder = Recorder()
    recorder.model_call("router", output_type="Answer")
    recorder.model_result(
        "router", input_tokens=41, output_tokens=17, parsed=True
    )
    recorder.model_call("summariser", output_type="Answer")
    # summariser never answered: the call hung.
    return recorder.trace


def test_a_call_that_never_answered_is_found() -> None:
    module = load("ch13", "e13_04_read_the_trace")
    assert module.unanswered(_recorded()) == ("summariser",)


def test_a_complete_trace_has_nothing_unanswered() -> None:
    module = load("ch13", "e13_04_read_the_trace")
    recorder = Recorder()
    recorder.model_call("router", output_type="Answer")
    recorder.model_result(
        "router", input_tokens=1, output_tokens=2, parsed=True
    )
    assert module.unanswered(recorder.trace) == ()


def test_an_empty_trace_is_not_a_special_case() -> None:
    module = load("ch13", "e13_04_read_the_trace")
    assert module.unanswered(Trace()) == ()
    assert module.spend(Trace()) == (0, 0)


def test_the_spend_adds_up_over_results_only() -> None:
    module = load("ch13", "e13_04_read_the_trace")
    assert module.spend(_recorded()) == (41, 17)
