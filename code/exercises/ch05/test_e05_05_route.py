from types import ModuleType

import pytest

from exercises._loader import load


def _module() -> ModuleType:
    return load("ch05", "e05_05_route")


def test_retry_patterns_including_the_guard() -> None:
    module = _module()
    assert module.route(module.Retry(0)) == "now"
    assert module.route(module.Retry(30)) == "in 30s"
    assert module.route(module.Retry(61)) == "later"
    assert module.route(module.Retry(60)) == "in 60s"


def test_a_class_pattern_ignores_the_fields_it_does_not_name() -> None:
    module = _module()
    assert module.route(module.Fail("no quota")) == "dead letter"
    assert module.route(module.Fail("")) == "dead letter"


def test_sequence_and_mapping_patterns() -> None:
    module = _module()
    assert module.route([]) == "batch of 0"
    assert module.route(["a", "b"]) == "batch of 2"
    assert module.route({"status": "active"}) == "keep"


def test_a_dotted_name_compares_where_a_bare_one_would_capture() -> None:
    module = _module()
    # If the mapping case had been written `case {"status": ACTIVE}` this
    # would return "keep" too, because the bare name matches anything.
    assert module.route({"status": "retired"}) == "drop"
    assert module.route("active") == "drop"


@pytest.mark.parametrize("value", [7, None, 3.5, object()])
def test_everything_else_is_dropped(value: object) -> None:
    module = _module()
    assert module.route(value) == "drop"
