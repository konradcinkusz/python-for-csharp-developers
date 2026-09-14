import sys

import pytest

from exercises._loader import load


def test_the_lock_only_costs_pure_python_work() -> None:
    module = load("ch01", "e01_03_which_pool")
    assert module.pick_pool("python", gil_enabled=True) == "processes"
    assert module.pick_pool("io", gil_enabled=True) == "threads"
    assert module.pick_pool("extension", gil_enabled=True) == "threads"


def test_without_the_lock_threads_answer_everything() -> None:
    module = load("ch01", "e01_03_which_pool")
    for workload in ("python", "io", "extension"):
        assert module.pick_pool(workload, gil_enabled=False) == "threads"


def test_the_default_reads_the_running_interpreter() -> None:
    module = load("ch01", "e01_03_which_pool")
    gil = sys._is_gil_enabled()  # pyright: ignore[reportPrivateUsage]
    assert module.pick_pool("python") == module.pick_pool(
        "python", gil_enabled=gil
    )


def test_an_unknown_workload_is_refused_rather_than_guessed() -> None:
    module = load("ch01", "e01_03_which_pool")
    with pytest.raises(ValueError):
        module.pick_pool("gpu", gil_enabled=True)
