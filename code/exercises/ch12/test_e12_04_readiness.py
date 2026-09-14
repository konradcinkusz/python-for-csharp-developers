"""Readiness goes first, liveness stays, and the drain has to finish."""

from __future__ import annotations

from typing import Any

import pytest

from exercises._loader import load


@pytest.fixture
def lifecycle() -> Any:
    return load("ch12", "e12_04_readiness").Lifecycle()


def test_shutdown_withdraws_readiness_and_keeps_liveness(
    lifecycle: Any,
) -> None:
    lifecycle.begin_shutdown()
    assert (lifecycle.ready, lifecycle.live) == (False, True)


def test_a_fresh_process_may_not_exit(lifecycle: Any) -> None:
    assert not lifecycle.may_exit


def test_it_may_not_exit_while_a_request_is_in_flight(
    lifecycle: Any,
) -> None:
    lifecycle.begin_request()
    lifecycle.begin_shutdown()
    assert not lifecycle.may_exit
    lifecycle.finish_request()
    assert lifecycle.may_exit


def test_finishing_never_drives_the_count_negative(
    lifecycle: Any,
) -> None:
    lifecycle.finish_request()
    assert lifecycle.in_flight == 0
