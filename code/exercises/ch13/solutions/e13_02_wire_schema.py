"""Reference solution for exercise 13.2."""

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
    schema = model.model_json_schema()
    schema["additionalProperties"] = False
    # A nested model is not nested in the schema: pydantic lifts it into
    # $defs and refers to it with $ref, so closing the top level closes
    # exactly one of the two objects a provider will check.
    for definition in schema.get("$defs", {}).values():
        definition["additionalProperties"] = False
    return schema
