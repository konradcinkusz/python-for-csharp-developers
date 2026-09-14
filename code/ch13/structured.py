"""One structured output, and the two ways pydantic will read it.

A model returns text. A structured output is that text parsed into a type
you declared, and in Python the type is a pydantic model. Everything an SDK
does for you here is the two calls at the bottom of this file: turn the
model into a JSON schema to send, and turn the reply back into the model.

    cd code && uv run python ch13/structured.py
"""

from __future__ import annotations

import json

from pydantic import BaseModel, ConfigDict, ValidationError


# --8<-- [start:models]
class Answer(BaseModel):
    """What the model is asked to fill in. Lax: pydantic's default."""

    summary: str
    severity: int
    needs_human: bool


class StrictAnswer(BaseModel):
    """The same four lines, with coercion turned off."""

    model_config = ConfigDict(strict=True)

    summary: str
    severity: int
    needs_human: bool
# --8<-- [end:models]


# A reply that is right in JSON and wrong in its types: every scalar has
# arrived as a string. Providers do this, and so do proxies that re-encode.
STRINGY = '{"summary": "disk full", "severity": "2", "needs_human": "true"}'


# --8<-- [start:schema]
def schema_for_the_wire(model: type[BaseModel]) -> dict[str, object]:
    """The schema an SDK sends, which is pydantic's plus two keys.

    `model_json_schema()` is the whole of it; a provider that refuses
    unknown fields wants `additionalProperties: false` as well, which
    pydantic does not emit because JSON Schema does not require it.
    """
    schema = model.model_json_schema()
    schema["additionalProperties"] = False
    return schema
# --8<-- [end:schema]


def main() -> int:
    schema = schema_for_the_wire(Answer)
    keys = ", ".join(sorted(k for k in schema if k != "properties"))
    print(f"schema keys   {keys}")
    print(f"required      {json.dumps(schema['required'])}")
    print()

    # --8<-- [start:validate]
    lax = Answer.model_validate_json(STRINGY)
    print(f"lax           {lax.severity!r} {lax.needs_human!r}")

    try:
        StrictAnswer.model_validate_json(STRINGY)
    except ValidationError as error:
        kinds = [e["type"] for e in error.errors()]
        print(f"strict        {error.error_count()} errors: {kinds}")
    # --8<-- [end:validate]
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
