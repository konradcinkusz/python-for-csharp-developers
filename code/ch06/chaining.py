"""Four ways to re-raise, and what each one leaves behind.

Run it from code/:

    uv run python ch06/chaining.py

C# attaches a stack trace to the throw site, so `throw ex;` truncates it and
`throw;` does not. Python attaches the traceback to the exception OBJECT, so
neither shape here truncates anything -- what differs is what the reader of
the failure is told about how the two exceptions are connected.

It prints frame names rather than the traceback itself, because a traceback
carries the absolute path of the file that raised, and the transcripts in
this book have to come out the same on your machine as on the one that
built the page.
"""

from __future__ import annotations

import traceback


class ConfigError(RuntimeError):
    """The domain error this module raises at its boundary."""


def port(settings: dict[str, str]) -> int:
    """Return the configured port. Raises KeyError when it is absent."""
    return int(settings["port"])


# --8<-- [start:shapes]
def raise_exc(settings: dict[str, str]) -> int:
    try:
        return port(settings)
    except KeyError as exc:
        raise exc  # the C# reflex: throw ex;


def raise_bare(settings: dict[str, str]) -> int:
    try:
        return port(settings)
    except KeyError:
        raise  # the C# reflex: throw;


def wrap_from(settings: dict[str, str]) -> int:
    try:
        return port(settings)
    except KeyError as exc:
        raise ConfigError("no port configured") from exc


def wrap_plain(settings: dict[str, str]) -> int:
    try:
        return port(settings)
    except KeyError:
        raise ConfigError("no port configured")  # noqa: B904
# --8<-- [end:shapes]


# --8<-- [start:report]
def frames(exc: BaseException) -> str:
    """The function names in an exception's own traceback, oldest first."""
    return ">".join(f.name for f in traceback.extract_tb(exc.__traceback__))


def describe(exc: BaseException) -> str:
    cause = type(exc.__cause__).__name__ if exc.__cause__ else "-"
    context = type(exc.__context__).__name__ if exc.__context__ else "-"
    return f"{frames(exc)} cause={cause} context={context}"
# --8<-- [end:report]


def main() -> None:
    for shape in (raise_exc, raise_bare, wrap_from, wrap_plain):
        try:
            shape({})
        except (KeyError, ConfigError) as exc:
            print(f"{shape.__name__:11}{describe(exc)}")


if __name__ == "__main__":
    main()
