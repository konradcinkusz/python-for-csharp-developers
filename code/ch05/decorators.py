"""A decorator runs. An attribute does not. That is the whole difference.

[Timed] in C# is metadata: the compiler records it, and it changes nothing
until something reflects over it and decides to act. @timed here is a
function call. It runs the moment the def statement finishes, it is handed
the function object, and whatever it returns is what the name now refers
to -- so a decorator is closer to ASP.NET Core middleware, wrapped round
the call, than to an attribute.

Run it from code/:

    uv run python ch05/decorators.py
"""

import functools
import time
from collections.abc import Callable

EVENTS: list[str] = []


# --8<-- [start:definition_time]
def announce[**P, T](fn: Callable[P, T]) -> Callable[P, T]:
    """Print once when the def below it finishes, and once per call."""
    EVENTS.append(f"decorating {fn.__name__}")

    @functools.wraps(fn)  # keeps __name__, __doc__ and __wrapped__
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        EVENTS.append(f"calling {fn.__name__}")
        return fn(*args, **kwargs)

    return wrapper


@announce
def parse(line: str) -> int:
    """The body never runs at definition time. The decorator does."""
    return len(line)
# --8<-- [end:definition_time]


# --8<-- [start:timing]
ELAPSED: list[float] = []


def timed[**P, T](fn: Callable[P, T]) -> Callable[P, T]:
    """The other half of what middleware does: measure the call.

    Nothing here prints a duration. A duration is a property of the
    machine, and this listing's output is a committed transcript the build
    compares on every run -- so the transcript reports how many calls were
    measured, and measure/ch05_concat.py is where a duration is allowed to
    reach the page, as a bound.
    """

    @functools.wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        start = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            ELAPSED.append(time.perf_counter() - start)

    return wrapper
# --8<-- [end:timing]


# --8<-- [start:retry]
def retry[**P, T](
    attempts: int,
    *,
    catching: type[Exception] = Exception,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """A decorator that takes arguments is a function returning a decorator.

    Three call levels, which is what @retry(3) means: retry(3) runs first
    and returns `decorate`, `decorate` is then applied to the function, and
    `wrapper` is what the name ends up bound to.
    """

    def decorate(fn: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            last: Exception | None = None
            for attempt in range(1, attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except catching as exc:
                    last = exc
                    EVENTS.append(f"attempt {attempt} failed: {exc}")
                    time.sleep(0)  # a real one would back off here
            assert last is not None
            raise last

        return wrapper

    return decorate
# --8<-- [end:retry]


calls = 0


@timed
@retry(3, catching=ConnectionError)
def flaky() -> str:
    global calls
    calls += 1
    if calls < 3:
        raise ConnectionError(f"refused (call {calls})")
    return "ok"


def main() -> int:
    print("Before a single call, the module has already recorded:")
    for event in EVENTS:
        print(f"    {event}")
    EVENTS.clear()
    print("parse('abc') returns", parse("abc"))
    print("flaky() returns", flaky())
    print("and calling them added:")
    for event in EVENTS:
        print(f"    {event}")
    print("parse.__name__ is still", parse.__name__)
    # Stacked decorators apply bottom-up: retry wraps flaky, then timed
    # wraps that, so the timing covers all of the attempts rather than
    # one of them.
    print(f"timed calls measured: {len(ELAPSED)}, "
          f"all non-negative: {all(e >= 0 for e in ELAPSED)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
