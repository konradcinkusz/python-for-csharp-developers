"""Four ways the checker stops seeing, in one file.

Run it from code/:

    uv run python ch03/where_it_lies.py

Every function below declares that it returns an int. Every one of them
returns a str. The file runs, and the two checkers this book pins do not
agree about how much of it is wrong -- which is the measurement in
code/measure/checkers.py, and the reason the book pins both.

The first two are Any arriving without anyone deciding anything. The last
two are you telling the checker to stop looking, which it will always do.
"""

import json
from typing import Any, cast


def read_port(blob: str) -> int:
    """json.loads is annotated to return Any, so settings is Any, so the
    subscript is Any, so returning it satisfies any declared type at all."""
    settings = json.loads(blob)
    return settings["port"]


def scaled(reading: Any) -> int:
    """A stand-in for a package that ships no type information: whatever
    comes back is Any, and Any times two is Any."""
    return reading * 2


def forced(blob: str) -> int:
    """cast() generates no code and checks nothing. It is an assertion to
    the checker, and you now own it."""
    return cast(int, json.loads(blob)["port"])


def silenced() -> int:
    """The error is real, visible and on one line. The comment removes it
    from the report without removing it from the program."""
    return "8080"  # type: ignore[return-value]


def main() -> None:
    for label, value in (
        ("read_port", read_port('{"port": "8080"}')),
        ("scaled", scaled("ab")),
        ("forced", forced('{"port": "8080"}')),
        ("silenced", silenced()),
    ):
        print(f"  {label:<10} declared int, returned {type(value).__name__}")


if __name__ == "__main__":
    main()
