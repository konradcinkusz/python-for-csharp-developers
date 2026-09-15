"""Reference solution for exercise 5.2."""

import itertools
from collections.abc import Iterator
from dataclasses import dataclass

SCANNED: list[str] = []


@dataclass(frozen=True)
class Job:
    name: str
    seconds: int
    status: str


def scan(job: Job) -> Job:
    SCANNED.append(job.name)
    return job


def worst(jobs: list[Job], limit: int) -> list[str]:
    """Failed jobs, longest first, as a list that has already run."""
    failed = sorted(
        (scan(job) for job in jobs if job.status == "failed"),
        key=lambda job: job.seconds,
        reverse=True,
    )
    return [f"{job.name} ({job.seconds}s)" for job in failed][:limit]


def stream(jobs: list[Job], limit: int) -> Iterator[str]:
    """Failed jobs, source order, deferred until the caller iterates."""
    scanned = (scan(job) for job in jobs if job.status == "failed")
    return itertools.islice(
        (f"{job.name} ({job.seconds}s)" for job in scanned), limit
    )
