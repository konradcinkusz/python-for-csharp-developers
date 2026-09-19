"""A closure captures the variable, not its value. C# fixed this in 5.0.

If you started .NET before C# 5, you have met this exact bug in a foreach
loop and you remember the fix: copy the loop variable into a fresh local
inside the body. C# 5 made foreach do that for you; Python never did, and
a comprehension is a loop.

Run it from code/:

    uv run python ch05/late_binding.py
"""

import functools
from collections.abc import Callable


# --8<-- [start:trap]
def build_broken() -> list[Callable[[], int]]:
    """Three closures over one variable. All three see its last value.

    The noqa is the point rather than an escape: ruff's B023 -- "function
    definition does not bind loop variable" -- refuses this line, so the
    linter Chapter 2 put in the toolchain finds the bug before any test
    does. It has to be silenced here to print the bug at all.
    """
    return [lambda: i for i in range(3)]  # noqa: B023
# --8<-- [end:trap]


# --8<-- [start:fixes]
def build_default_arg() -> list[Callable[[], int]]:
    """A default argument is evaluated once, at def -- so it captures now.

    The one-liner you will meet in the wild is `lambda i=i: i`, which is
    this with the names collapsed. Written out, the fresh local is the
    same move C# 5 made foreach do for you.
    """
    handlers: list[Callable[[], int]] = []
    for i in range(3):
        def handler(bound: int = i) -> int:
            return bound
        handlers.append(handler)
    return handlers


def identity(value: int) -> int:
    return value


def build_partial() -> list[Callable[[], int]]:
    """functools.partial binds the argument at the moment partial runs."""
    return [functools.partial(identity, i) for i in range(3)]
# --8<-- [end:fixes]


def main() -> int:
    for name, build in (
        ("lambda: i", build_broken),
        ("lambda i=i: i", build_default_arg),
        ("partial(f, i)", build_partial),
    ):
        print(f"{name:>15}  ->  {[fn() for fn in build()]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
