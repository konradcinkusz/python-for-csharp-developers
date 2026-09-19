"""Where the state lives, and the two ways that bites.

A C# static field and a Python class attribute are not the same thing, and
the difference is not that one is shared. Both are shared. The difference
is that a class attribute is READABLE THROUGH THE INSTANCE, with no
qualification and no warning -- so `self.seen` finds the class's object,
and mutating it mutates it for every instance that will ever exist.

Run it from code/:

    uv run python ch04/state.py
"""

from __future__ import annotations

from dataclasses import dataclass, field


# --8<-- [start:shared]
class RegistryBroken:
    """`seen` looks like a field and is a static. Every instance shares it.

    Nothing about `self.seen.append(name)` says so. The lookup walks the
    instance's own __dict__ first, finds nothing, walks the class's, finds
    the list, and mutates that -- so the second instance starts with the
    first one's data.
    """

    seen: list[str] = []

    def record(self, name: str) -> None:
        self.seen.append(name)


class Registry:
    """Per-instance state is created in __init__, and only there."""

    def __init__(self) -> None:
        self.seen: list[str] = []

    def record(self, name: str) -> None:
        self.seen.append(name)


def new_log() -> list[str]:
    """A named factory with a return type.

    `default_factory=list` is what everyone writes and what pyright
    strict refuses: a bare `list` is list[Unknown] to it, and the checker
    is right that nothing has said what goes in. Naming the factory is
    the fix, and it reads better than the cast would.
    """
    return []


@dataclass
class RegistryDataclass:
    """@dataclass refuses the broken spelling outright.

    A mutable default in a dataclass raises ValueError at class creation
    time, naming default_factory. It is the one place in the language that
    stops this bug before it runs, which is worth knowing because the
    plain class above is the spelling it cannot see.
    """

    seen: list[str] = field(default_factory=new_log)
# --8<-- [end:shared]


# --8<-- [start:aliasing]
def rows_broken(n: int) -> list[list[int]]:
    """One list, n times. `*` copies the reference, not the object."""
    return [[]] * n


def rows(n: int) -> list[list[int]]:
    """n lists. The comprehension evaluates its body once per item."""
    return [[] for _ in range(n)]
# --8<-- [end:aliasing]


def main() -> int:
    a, b = RegistryBroken(), RegistryBroken()
    a.record("first")
    b.record("second")
    print(f"broken       a.seen {a.seen}  b.seen {b.seen}")
    print(f"             same object: {a.seen is b.seen}")
    print(f"             and on the class: {RegistryBroken.seen}")

    c, d = Registry(), Registry()
    c.record("first")
    d.record("second")
    print(f"fixed        c.seen {c.seen}  d.seen {d.seen}")

    try:

        @dataclass
        class Bad:
            seen: list[str] = []  # noqa: RUF008
    except ValueError as exc:
        print(f"dataclass    ValueError: {str(exc)[:46]}...")

    broken = rows_broken(3)
    broken[0].append(1)
    good = rows(3)
    good[0].append(1)
    print()
    print(f"[[]] * 3     {broken}   distinct: {len({id(r) for r in broken})}")
    print(f"comprehension {good}   distinct: {len({id(r) for r in good})}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
