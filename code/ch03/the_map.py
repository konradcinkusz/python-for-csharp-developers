"""Two pieces of the map that do not translate one for one.

Run it from code/:

    uv run python ch03/the_map.py

Generics look like C# generics and declare their variance differently.
Narrowing looks like pattern matching and has two spellings, one of which
does half the job.
"""

from typing import TypeGuard, TypeIs

# --8<-- [start:generics]


class Reader[T]:
    """PEP 695: the type parameter is declared on the class, no TypeVar
    and no import. T is used only in an output position here."""

    def __init__(self, item: T) -> None:
        self._item = item

    def read(self) -> T:
        return self._item


class Sink[T]:
    """The same syntax, and T is used only in an input position."""

    def write(self, item: T) -> None:
        print(f"  wrote {item!r}")


def read_any(reader: Reader[object]) -> object:
    return reader.read()


def write_str(sink: Sink[str]) -> None:
    sink.write("x")


def variance() -> None:
    # Neither class said `out` or `in`. The checker reads which positions
    # T appears in and infers the variance from that, so a Reader[str]
    # goes where a Reader[object] is wanted and a Sink[object] goes where
    # a Sink[str] is wanted. Swap the two arguments and it refuses.
    print(" ", read_any(Reader("covariant by inference")))
    write_str(Sink[object]())


# --8<-- [end:generics]

# --8<-- [start:narrowing]


def looks_like_str(value: str | int) -> TypeIs[str]:
    """TypeIs, not TypeGuard. The difference is the else branch."""
    return isinstance(value, str)


def length_with_typeis(value: str | int) -> int:
    if looks_like_str(value):
        return len(value)
    # TypeIs narrows BOTH branches, so value is an int here and the
    # checker needs nothing further from us.
    return value


def guards_str(value: str | int) -> TypeGuard[str]:
    """The older spelling. Same body, same answer at run time."""
    return isinstance(value, str)


def length_with_typeguard(value: str | int) -> int:
    if guards_str(value):
        return len(value)
    # TypeGuard narrows only the positive branch, so the checker still
    # believes value is str | int here. Delete the second check and the
    # line below stops type-checking; that is the whole difference.
    return value if isinstance(value, int) else 0


def host_of(settings: dict[str, str]) -> str | None:
    """T | None is a union, and the checker will not let you forget it.
    Where C# has an annotation on a reference type, Python has a type
    that is genuinely two types until you narrow it."""
    return settings.get("host")


def describe(settings: dict[str, str]) -> str:
    host = host_of(settings)
    if host is None:
        return "no host configured"
    # Narrowed to str by the branch above: .upper() is allowed here and
    # is an error one line higher up.
    return host.upper()


# --8<-- [end:narrowing]


def main() -> None:
    print("Variance, inferred rather than declared:")
    variance()
    print("Narrowing:")
    print("  length_with_typeis('hello') ->", length_with_typeis("hello"))
    print("  length_with_typeis(7)       ->", length_with_typeis(7))
    print("  describe({})                ->", describe({}))
    print("  describe({'host': 'db'})    ->", describe({"host": "db"}))


if __name__ == "__main__":
    main()
