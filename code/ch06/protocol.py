"""Three exceptions that are not failures, and a fourth thing that is not one.

Run it from code/:

    uv run python ch06/protocol.py

KeyError, StopIteration and AttributeError are how three of Python's
protocols say "no". Each is raised on an ordinary path, caught by the
machinery one level up, and never reaches you -- so a handler that treats
any of them as a fault is handling normal operation.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator


# --8<-- [start:forloop]
def my_for(items: Iterable[str]) -> list[str]:
    """What `for item in items` compiles to, written out.

    The loop ends because next() RAISES. There is no end-of-sequence flag
    and nothing returns false; StopIteration is the terminating condition.
    """
    it: Iterator[str] = iter(items)
    seen: list[str] = []
    while True:
        try:
            seen.append(next(it))
        except StopIteration:
            return seen
# --8<-- [end:forloop]


# --8<-- [start:getattr]
def duck_type(value: object, name: str) -> str:
    """hasattr() is a try/except AttributeError with the answer discarded."""
    try:
        attr: object = getattr(value, name)
    except AttributeError:
        return f"no {name}()"
    return f"{name}() is {type(attr).__name__}"
# --8<-- [end:getattr]


# --8<-- [start:truthiness]
def describe(rows: list[str] | None) -> str:
    """Two different questions that a C# habit runs together.

    `if rows:` asks whether there is anything to do. `if rows is not None:`
    asks whether the caller passed a list at all. An empty list answers the
    first with no and the second with yes.
    """
    present = rows is not None
    has_work = bool(rows)
    return f"present={present} has_work={has_work}"
# --8<-- [end:truthiness]


def main() -> None:
    print("my_for:", my_for(["a", "b"]))
    print("dict.get is the same shape:", {"a": 1}.get("zz", "default"))

    class Handle:
        def close(self) -> None: ...

    print("duck_type(Handle()):", duck_type(Handle(), "close"))
    print("duck_type(42):      ", duck_type(42, "close"))

    for rows in (None, [], ["one"]):
        print(f"describe({rows!r:7}) -> {describe(rows)}")


if __name__ == "__main__":
    main()
