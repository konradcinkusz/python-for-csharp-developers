"""Exercise 13.2 -- the schema a provider will accept.

An SDK's structured-output call sends the JSON schema of the model you hand
it. pydantic emits a schema that is correct JSON Schema; a provider that
promises to return nothing but your fields wants one more key on every
object in it -- `additionalProperties: false` -- and a nested model means
there is more than one object.

Write `wire_schema` so that every object in the schema carries it,
including the ones under `$defs`.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class Service(BaseModel):
    name: str
    tier: int


class Reply(BaseModel):
    summary: str
    service: Service


def wire_schema(model: type[BaseModel]) -> dict[str, Any]:
    """`model`'s JSON schema, with every object closed to extra fields."""
    raise NotImplementedError("your turn: replace this line")
