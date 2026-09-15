"""The payoff: one model call, typed at both ends, that a service can hold.

Typed input in, typed output out, a timeout that is not the SDK's ten-minute
default, and two trace events. Nothing here is specific to a provider and
nothing is specific to an agent framework: this is the whole of what chapter
9's service needs in order to have a model in it.

    cd code && uv run python ch13/call_model.py
"""

from __future__ import annotations

from fake_provider import fake_provider
from openai import APITimeoutError, OpenAI
from pydantic import BaseModel

from trace_assert import Recorder


# --8<-- [start:types]
class Ask(BaseModel):
    """What the caller hands in. A service validates this at its edge."""

    question: str
    incident_id: int


class Answer(BaseModel):
    """What the caller gets back. The provider never sees this class --
    it sees the JSON schema pydantic makes out of it."""

    summary: str
    severity: int
    needs_human: bool
# --8<-- [end:types]


class ModelUnavailableError(RuntimeError):
    """The one error a caller has to handle, whatever the provider was.

    Named `...Error` and not `...Exception`: ruff's N818 enforces the
    Python convention, and the base class is already called an exception.
    """


# --8<-- [start:call]
def call_model(
    client: OpenAI,
    ask: Ask,
    *,
    model: str,
    recorder: Recorder,
    timeout: float = 20.0,
) -> Answer:
    """One call. Typed in, typed out, bounded in time, recorded."""
    recorder.model_call(model, output_type=Answer.__name__)
    try:
        reply = client.responses.parse(
            model=model,
            input=f"Incident {ask.incident_id}: {ask.question}",
            text_format=Answer,
            timeout=timeout,
        )
    except APITimeoutError as error:
        # No model_result event: nothing came back, and a trace that
        # invents one cannot be used to assert that a call hung.
        raise ModelUnavailableError(f"{model} did not answer") from error

    answer = reply.output_parsed
    usage = reply.usage
    recorder.model_result(
        model,
        input_tokens=usage.input_tokens if usage else 0,
        output_tokens=usage.output_tokens if usage else 0,
        parsed=answer is not None,
    )
    if answer is None:
        raise ModelUnavailableError(f"{model} returned no parsable answer")
    return answer
# --8<-- [end:call]


def main() -> int:
    recorder = Recorder()
    with fake_provider() as base_url:
        client = OpenAI(api_key="not-a-real-key", base_url=base_url,
                        max_retries=0)
        answer = call_model(
            client,
            Ask(question="why did it page?", incident_id=41),
            model="fake-provider",
            recorder=recorder,
        )

    print(f"type          {type(answer).__name__}")
    print(f"severity      {answer.severity!r}")
    print(f"needs_human   {answer.needs_human!r}")
    print()
    for event in recorder.trace.events:
        # The event's NAME is the kind -- `model_call`, `model_result` --
        # and the model is a tag, which is the way round the assertions
        # read it. See `Recorder` for why.
        print(f"{event.name:13} {event.tags.get('model', '')}")
        for key, value in event.tags.items():
            if key != "model":
                print(f"{'':13}   {key:14} {value!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
