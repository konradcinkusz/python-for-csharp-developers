"""Errors at the boundary: two libraries' failures, one domain hierarchy.

Run it from code/:

    uv run python ch06/boundary.py

Nothing here touches the network. The httpx response is constructed in
process, which is also how you test this code: raise_for_status() is a pure
function of the status line.
"""

from __future__ import annotations

import httpx
from pydantic import BaseModel, ValidationError


class Job(BaseModel):
    id: int
    retries: int


# --8<-- [start:hierarchy]
class JobError(Exception):
    """Anything this module raises. Catch this if you catch anything."""


class JobUnavailableError(JobError):
    """The service answered, and not with a job."""


class JobMalformedError(JobError):
    """The service answered with a job this version cannot read."""
# --8<-- [end:hierarchy]


# --8<-- [start:translate]
def parse_job(response: httpx.Response) -> Job:
    """Turn one HTTP response into a Job.

    Raises:
        JobUnavailableError: the status was not a success.
        JobMalformedError: the body was not a job.

    Nothing in the signature says that. A docstring is the only place
    Python has to put it, and nothing checks that it is true.
    """
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise JobUnavailableError(f"HTTP {exc.response.status_code}") from exc
    try:
        return Job.model_validate_json(response.text)
    except ValidationError as exc:
        first = exc.errors()[0]
        where = ".".join(str(part) for part in first["loc"]) or "<body>"
        raise JobMalformedError(f"{where}: {first['msg']}") from exc
# --8<-- [end:translate]


# --8<-- [start:batch]
def parse_many(
    responses: list[httpx.Response],
) -> tuple[list[Job], list[JobError]]:
    """Parse a batch, and answer for every row rather than the first.

    This is the shape a Result type is reaching for, and it needs no Result
    type: a caller who wants one answer per row gets two lists. Inside a
    call chain, where the caller has nothing useful to do with a failure,
    raise instead -- an Ok/Err wrapper there costs a branch at every call
    site and discards the traceback that would have named the line.
    """
    done: list[Job] = []
    failed: list[JobError] = []
    for response in responses:
        try:
            done.append(parse_job(response))
        except JobError as exc:
            failed.append(exc)
    return done, failed
# --8<-- [end:batch]


def reply(status: int, body: str) -> httpx.Response:
    request = httpx.Request("GET", "https://jobs.invalid/1")
    return httpx.Response(status, text=body, request=request)


def main() -> None:
    good = reply(200, '{"id": 1, "retries": 0}')
    for response in (good, reply(503, ""), reply(200, '{"id": "x"}')):
        try:
            print(f"{response.status_code}: {parse_job(response)}")
        except JobError as exc:
            print(f"{response.status_code}: {type(exc).__name__}: {exc} "
                  f"<- {type(exc.__cause__).__name__}")

    done, failed = parse_many([good, reply(404, ""), good])
    print(f"batch: {len(done)} parsed, {len(failed)} failed "
          f"({[type(e).__name__ for e in failed]})")


if __name__ == "__main__":
    main()
