"""Exercise 5.3 -- the same query, eager and deferred.

`worst` must return a list: the failed jobs, longest first, projected to
"name (Ns)", at most `limit` of them. `stream` must return an iterator over
the failed jobs in the order given, projected the same way, at most `limit`
of them -- and it must not have touched the source when it returns.

SCANNED records every job the pipeline looks at. The test uses it to prove
which of the two has already run, so build both out of the source given
rather than out of a list you materialised first.
"""

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
    raise NotImplementedError("your turn: replace this line")


def stream(jobs: list[Job], limit: int) -> Iterator[str]:
    """Failed jobs, source order, deferred until the caller iterates."""
    raise NotImplementedError("your turn: replace this line")
