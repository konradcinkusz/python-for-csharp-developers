"""with is using, and then contextlib gives you the three things it lacks.

using(var x = ...) needs a type that implements IDisposable, which means a
class. Python's `with` needs a type with __enter__ and __exit__ -- and
contextlib.contextmanager builds one out of a generator, so the common
case is a function with a yield in the middle rather than a class. Two
further differences worth having: __exit__ SEES the exception and may
swallow it, which Dispose cannot; and ExitStack holds a number of contexts
that is not known until run time, which nested using statements cannot.

Run it from code/:

    uv run python ch05/context.py
"""

import contextlib
from collections.abc import Generator

LOG: list[str] = []


# --8<-- [start:contextmanager]
@contextlib.contextmanager
def span(name: str) -> Generator[str]:
    """Everything before the yield is __enter__; the finally is __exit__.

    Generator[str], not the Iterator[str] every tutorial writes: pyright's
    typeshed marks that overload deprecated, with the message "Annotating
    the return type as `-> Iterator[Foo]` with `@contextmanager` is
    deprecated. Use `-> Generator[Foo]` instead."

    The finally is not decoration. Without it an exception raised in the
    body propagates out of the yield and the cleanup never runs -- which
    is the one way this is easier to get wrong than a using statement.
    """
    LOG.append(f"enter {name}")
    try:
        yield name
    finally:
        LOG.append(f"exit {name}")
# --8<-- [end:contextmanager]


# --8<-- [start:exitstack]
def open_all(names: list[str]) -> list[str]:
    """A number of contexts not known until run time, unwound in order."""
    with contextlib.ExitStack() as stack:
        return [stack.enter_context(span(name)) for name in names]
# --8<-- [end:exitstack]


def main() -> int:
    LOG.clear()
    with span("request") as name:
        LOG.append(f"body of {name}")
    print("plain:", LOG)

    LOG.clear()
    with contextlib.suppress(ZeroDivisionError), span("risky"):
        _ = 1 // 0
    print("exception:", LOG, "-- and suppress ate it")

    LOG.clear()
    print("stacked:", open_all(["a", "b", "c"]))
    print("order:", LOG)

    # A contextmanager is also a decorator, because contextlib builds one
    # that inherits ContextDecorator. C# has no equivalent of that at all.
    LOG.clear()

    @span("decorated")
    def work() -> str:
        return "done"

    print("as a decorator:", work(), LOG)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
