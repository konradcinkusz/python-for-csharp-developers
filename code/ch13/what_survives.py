"""Seven replies that are valid JSON and wrong, and what gets through.

The cost of validation is the question everybody asks. What it buys is the
question worth asking, and it is answerable exactly: take every way one
structured output goes wrong without stopping it being JSON, and count what
each strategy lets past.

The corpus below is the one experiment E8 times, imported from here rather
than copied, so the table on the page and the measurement cannot disagree.

    cd code && uv run python ch13/what_survives.py
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass

from pydantic import ValidationError
from structured import Answer, StrictAnswer


# --8<-- [start:plain]
@dataclass
class PlainAnswer:
    """What a C# engineer writes first: a record, filled from a dict.

    `System.Text.Json` would refuse a string where an int is declared.
    This refuses nothing: a dataclass generates `__init__`, `__eq__` and
    `__repr__`, and checks not one of its annotations at run time.
    """

    summary: str
    severity: int
    needs_human: bool
# --8<-- [end:plain]


# Labelled, because a count is only useful if you can see which one.
MALFORMED: list[tuple[str, str]] = [
    ("severity as a string",
     '{"summary": "d", "severity": "2", "needs_human": false}'),
    ("needs_human as a string",
     '{"summary": "d", "severity": 2, "needs_human": "true"}'),
    ("severity missing",
     '{"summary": "d", "needs_human": false}'),
    ("severity null",
     '{"summary": "d", "severity": null, "needs_human": false}'),
    ("summary as a number",
     '{"summary": 7, "severity": 2, "needs_human": false}'),
    ("severity 2.5",
     '{"summary": "d", "severity": 2.5, "needs_human": false}'),
    ("an extra field",
     '{"summary": "d", "severity": 2, "needs_human": false, "conf": 0.9}'),
]


# --8<-- [start:strategies]
def by_lax(raw: str) -> object:
    """pydantic as it comes."""
    return Answer.model_validate_json(raw)


def by_strict(raw: str) -> object:
    """pydantic with coercion off."""
    return StrictAnswer.model_validate_json(raw)


def by_plain(raw: str) -> object:
    """The standard library, and a type that does not check itself."""
    return PlainAnswer(**json.loads(raw))


STRATEGIES: dict[str, Callable[[str], object]] = {
    "lax": by_lax,
    "strict": by_strict,
    "plain": by_plain,
}


def rejects(strategy: Callable[[str], object], raw: str) -> bool:
    """Did it refuse the payload, by any means at all? A TypeError from a
    missing keyword argument counts: the question is what gets through."""
    try:
        strategy(raw)
    except (ValidationError, TypeError, KeyError, ValueError):
        return True
    return False
# --8<-- [end:strategies]


def main() -> int:
    names = list(STRATEGIES)
    header = " ".join(f"{n:>7}" for n in names)
    print(f"{'what is wrong with it':25} {header}")
    for label, raw in MALFORMED:
        marks = [
            "reject" if rejects(STRATEGIES[n], raw) else "LET IN"
            for n in names
        ]
        print(f"{label:25} " + " ".join(f"{m:>7}" for m in marks))

    totals = [
        sum(rejects(STRATEGIES[n], raw) for _, raw in MALFORMED)
        for n in names
    ]
    print(f"{'rejected of ' + str(len(MALFORMED)):25} "
          + " ".join(f"{t:>7}" for t in totals))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
