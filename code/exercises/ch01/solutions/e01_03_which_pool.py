"""Reference solution for exercise 1.3."""

import sys

WORKLOADS = ("python", "io", "extension")


def _gil_enabled() -> bool:
    # Private by name only: the documentation names it as the probe.
    probe = sys._is_gil_enabled  # pyright: ignore[reportPrivateUsage]
    return probe()


def pick_pool(workload: str, gil_enabled: bool | None = None) -> str:
    """Return "threads" or "processes" for `workload` on this build."""
    if workload not in WORKLOADS:
        raise ValueError(
            f"unknown workload {workload!r}; expected one of {WORKLOADS}"
        )
    if gil_enabled is None:
        gil_enabled = _gil_enabled()
    # Only one cell of the table says "processes": pure Python bytecode on
    # a build that serialises it. Everything else either never holds the
    # lock or no longer has one to hold.
    if gil_enabled and workload == "python":
        return "processes"
    return "threads"
