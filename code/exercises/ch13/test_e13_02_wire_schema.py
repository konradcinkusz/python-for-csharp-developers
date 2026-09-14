from typing import Any

from exercises._loader import load


def _schema() -> dict[str, Any]:
    module = load("ch13", "e13_02_wire_schema")
    return module.wire_schema(module.Reply)


def test_the_top_level_object_is_closed() -> None:
    assert _schema()["additionalProperties"] is False


def test_the_nested_model_is_closed_too() -> None:
    # The one the top level alone does not reach: a nested model is a
    # separate object under $defs, and a provider checks all of them.
    defs = _schema()["$defs"]
    assert defs, "a nested model should have produced a $defs entry"
    for name, node in defs.items():
        assert node["additionalProperties"] is False, name


def test_pydantics_own_schema_is_left_otherwise_intact() -> None:
    schema = _schema()
    assert schema["type"] == "object"
    assert sorted(schema["required"]) == ["service", "summary"]
