"""Both kinds of record, one renderer, and the context on both."""

from __future__ import annotations

import io
import json
import logging

import pytest
import structlog

from exercises._loader import load


@pytest.fixture
def rendered() -> list[dict[str, object]]:
    module = load("ch12", "e12_01_bootstrap")
    stream = io.StringIO()
    module.configure_logging(stream)
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id="abc")
    try:
        structlog.get_logger("app").info("mine")
        logging.getLogger("someone.else").warning("theirs")
    finally:
        structlog.contextvars.clear_contextvars()
        logging.getLogger().handlers = []
        structlog.reset_defaults()
    return [
        json.loads(line)
        for line in stream.getvalue().splitlines()
        if line.strip()
    ]


def test_both_records_are_json(
    rendered: list[dict[str, object]],
) -> None:
    assert [r["event"] for r in rendered] == ["mine", "theirs"]


def test_both_records_carry_the_level(
    rendered: list[dict[str, object]],
) -> None:
    assert [r["level"] for r in rendered] == ["info", "warning"]


def test_the_stdlib_record_carries_the_request_id(
    rendered: list[dict[str, object]],
) -> None:
    # The one that is easy to get wrong: a foreign_pre_chain without
    # merge_contextvars renders the library's line with no context at all.
    assert [r.get("request_id") for r in rendered] == ["abc", "abc"]
