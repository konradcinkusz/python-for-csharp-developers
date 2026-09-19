from types import ModuleType
from typing import Any

from exercises._loader import load


def _module() -> ModuleType:
    module = load("ch05", "e05_03_pipeline")
    module.SCANNED.clear()
    return module


def _jobs(module: ModuleType) -> list[Any]:
    return [
        module.Job("build", 42, "ok"),
        module.Job("test", 310, "failed"),
        module.Job("lint", 4, "failed"),
        module.Job("deploy", 91, "failed"),
    ]


def test_worst_orders_by_duration_and_limits() -> None:
    module = _module()
    assert module.worst(_jobs(module), 2) == ["test (310s)", "deploy (91s)"]


def test_worst_has_already_run_when_it_returns() -> None:
    module = _module()
    module.worst(_jobs(module), 2)
    assert module.SCANNED == ["test", "lint", "deploy"]


def test_stream_has_not_run_when_it_returns() -> None:
    module = _module()
    module.stream(_jobs(module), 2)
    assert module.SCANNED == []


def test_stream_yields_in_source_order_and_is_exhausted_once() -> None:
    module = _module()
    lazy = module.stream(_jobs(module), 2)
    assert list(lazy) == ["test (310s)", "lint (4s)"]
    assert module.SCANNED == ["test", "lint"]
    assert list(lazy) == []
