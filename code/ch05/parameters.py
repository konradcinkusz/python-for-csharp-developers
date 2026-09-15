"""params, optional and named arguments -- and the two Python has extra.

*args is params. **kwargs has no C# equivalent at all: a caller may pass
names the callee never declared. And Python can make a parameter
positional-only (before /) or keyword-only (after *), which C# cannot. In
C# every parameter name is part of the public surface forever, because any
caller may pass it by name; / is how Python takes that back.

Run it from code/:

    uv run python ch05/parameters.py
"""

import functools
from collections.abc import Callable


# --8<-- [start:signature]
def render(
    template: str,          # positional or keyword, like every C# parameter
    /,                      # everything BEFORE this is positional-only
    *values: int,           # params int[]
    indent: int = 0,        # keyword-only: it is declared after *values
    **options: str,         # no C# equivalent: undeclared names, by name
) -> str:
    """All five kinds of parameter Python has, in one signature."""
    body = template.format(*values)
    flags = "".join(f" [{k}={v}]" for k, v in sorted(options.items()))
    return " " * indent + body + flags
# --8<-- [end:signature]


# --8<-- [start:refusals]
def fetch(url: str, /, *, retries: int = 0) -> str:
    """url may never be passed by name; retries may never be positional."""
    return f"GET {url} (retries={retries})"
# --8<-- [end:refusals]


# --8<-- [start:partial]
def connect(host: str, port: int, *, timeout: float) -> str:
    return f"{host}:{port} t={timeout}"


# functools.partial is the closest thing to a captured delegate: it binds
# some arguments now and returns something callable. Placeholder, new in
# Python 3.14, lets a partial skip a positional argument and bind a later
# one, which no earlier version could do.
local: Callable[[int], str] = functools.partial(
    connect, "localhost", timeout=2.0
)
# Placeholder, new in Python 3.14, lets a partial skip a positional
# argument and bind a later one -- no earlier version could. It runs, and
# the type stubs do not model it yet: typeshed declares Placeholder and
# partial's overloads accept nothing of its type. So the two suppressions
# below are what using a run-time feature ahead of its stubs looks like,
# and they are measured against the pinned pyright rather than assumed.
on_8080 = functools.partial(
    connect,
    functools.Placeholder,  # pyright: ignore[reportArgumentType]
    8080,
    timeout=2.0,
)
# --8<-- [end:partial]


def main() -> int:
    print(render("{0}/{1}", 3, 4, indent=2, colour="red", bold="yes"))
    print(local(8080))
    # Two suppressions, for the one reason given above the partial.
    print(on_8080("example.internal"))  # pyright: ignore
    print(fetch("/health", retries=2))
    # pyright refuses both of these before anything runs, which is the
    # whole argument for the two markers; the ignores are what let the
    # listing show the run-time half as well.
    try:
        fetch(url="/health")  # pyright: ignore[reportCallIssue]
    except TypeError as exc:
        print("url passed by name -> TypeError")
        print(exc)
    try:
        fetch("/health", 2)  # pyright: ignore[reportCallIssue]
    except TypeError as exc:
        print("retries passed positionally -> TypeError")
        print(exc)
    # And the reason / is worth the character: with **options present, the
    # same mistake against a name that is NOT positional-only is absorbed
    # in silence rather than refused.
    print(render("ok", template="ignored"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
