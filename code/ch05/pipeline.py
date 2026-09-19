"""A comprehension is not LINQ. One of them has already run.

A LINQ query is an IEnumerable: nothing happens until something
enumerates it, and enumerating it twice runs the whole pipeline twice. A
list comprehension is the opposite -- it has run by the time the closing
bracket is passed, and the result is a list you may walk as often as you
like. A generator expression is deferred like LINQ, and then differs from
it in the way that bites: it is exhausted by the first pass.

Run it from code/:

    uv run python ch05/pipeline.py
"""

import itertools
from collections.abc import Iterator
from dataclasses import dataclass


@dataclass(frozen=True)
class Job:
    name: str
    seconds: int
    status: str


JOBS = [
    Job("build", 42, "ok"),
    Job("test", 310, "failed"),
    Job("lint", 4, "failed"),
    Job("deploy", 91, "failed"),
]

SEEN: list[str] = []


def scan(job: Job) -> Job:
    """Records every job the pipeline actually looks at."""
    SEEN.append(job.name)
    return job


# --8<-- [start:eager]
def worst(jobs: list[Job], limit: int) -> list[str]:
    """The LINQ pipeline, as a comprehension. It has run when it returns.

    Where LINQ chains Where/OrderByDescending/Select/Take, a comprehension
    puts the projection first, the source second and the filter last, and
    the ordering stays outside it -- Python has no OrderBy clause, because
    sorted() already is one. Note that sorting is a barrier in both
    languages: it cannot answer until it has seen every element, so a
    pipeline that orders has run whatever the rest of it promised.
    """
    failed = sorted(
        (scan(job) for job in jobs if job.status == "failed"),
        key=lambda job: job.seconds,
        reverse=True,
    )
    return [f"{job.name} ({job.seconds}s)" for job in failed][:limit]
# --8<-- [end:eager]


# --8<-- [start:deferred]
def failures(jobs: list[Job], limit: int) -> Iterator[str]:
    """The same filter and projection, deferred. islice is Take.

    No ordering, because ordering would force it. Nothing here has run
    when this returns, and everything here runs exactly once, on the
    first pass over the result.
    """
    scanned = (scan(job) for job in jobs if job.status == "failed")
    named = (f"{job.name} ({job.seconds}s)" for job in scanned)
    return itertools.islice(named, limit)
# --8<-- [end:deferred]


def main() -> int:
    SEEN.clear()
    eager = worst(JOBS, 2)
    print("comprehension: scanned", SEEN, "before it returned")
    print("  pass 1:", eager)
    print("  pass 2:", list(eager))

    SEEN.clear()
    lazy = failures(JOBS, 2)
    print("generator:     scanned", SEEN, "before it returned")
    print("  pass 1:", list(lazy), "having scanned", SEEN)
    print("  pass 2:", list(lazy))

    # Building the report. += in a loop is the C# habit; join is the
    # Python one, and measure/ch05_concat.py measures what it costs.
    print("  report:", ", ".join(eager))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
