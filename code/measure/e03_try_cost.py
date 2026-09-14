#!/usr/bin/env python3
"""Experiment E3: what a `try` costs against a check, both paths.

The question chapter 6 rests on is a cost question -- Python raises where C#
checks, so how much does that cost? -- and a wall-clock answer to it is a
property of the machine that ran it. This book's rule is that a
machine-dependent residual is committed as a BOUND and never as a figure, so
this script measures the same question two ways and commits only the half
that is reproducible:

  * EXACT, and identical on any machine running the pinned interpreter: the
    number of bytecode instructions each shape actually executes, counted by
    tracing at opcode level, and the size of the exception table the `try`
    compiles into. CPython's compiler is platform-independent, so these are
    properties of the language version rather than of the hardware.

  * MEASURED HERE AND NOT COMMITTED: nanoseconds. The script prints its own
    machine's timings when you run it, and asserts BOUNDS on them that hold
    with a wide margin -- so a build on any machine either clears the bound
    or fails loudly. The bound is a decision recorded here; the timing is an
    observation, and only the decision reaches the page.

Run from code/:   uv run python measure/e03_try_cost.py
"""

from __future__ import annotations

import contextlib
import sys
import timeit
from collections.abc import Mapping
from pathlib import Path
from types import FrameType
from typing import Any

OUT = Path(__file__).resolve().parents[2] / "figures" / "values" / "e03.tex"

# Module level so timeit's `globals=globals()` can see it along with the
# three shapes below.
RATES = {"GBP": 1.0, "EUR": 1.17}

# The three shapes. They answer the same question about the same mapping and
# differ only in how they ask it.

# --8<-- [start:shapes]
def plain(rates: Mapping[str, float], code: str) -> float:
    return rates[code]


def lbyl(rates: Mapping[str, float], code: str) -> float:
    if code in rates:
        return rates[code]
    return 0.0


def eafp(rates: Mapping[str, float], code: str) -> float:
    try:
        return rates[code]
    except KeyError:
        return 0.0
# --8<-- [end:shapes]


# --8<-- [start:count]
def executed(fn: Any, *args: Any) -> int:
    """How many bytecode instructions a call to `fn` actually runs.

    Opcode tracing fires one event per instruction dispatched in the traced
    frame, so this counts the path taken rather than the code compiled -- a
    handler that does not run is not counted, which is the whole question.
    """
    target = fn.__code__
    n = 0

    def trace(frame: FrameType, event: str, _arg: Any) -> Any:
        nonlocal n
        if frame.f_code is not target:
            return None
        if event == "opcode":
            n += 1
        frame.f_trace_opcodes = True
        return trace

    sys.settrace(trace)
    try:
        with contextlib.suppress(KeyError):
            fn(*args)
    finally:
        sys.settrace(None)
    return n
# --8<-- [end:count]


def nanoseconds(stmt: str, number: int = 200_000) -> float:
    """The best of seven runs, in nanoseconds per call.

    `globals=` rather than a setup string: the shapes are already defined
    here, and importing them back into timeit's namespace would measure an
    import path as well as the call.
    """
    timed = timeit.repeat(stmt, number=number, repeat=7, globals=globals())
    return min(timed) / number

# The two bounds this script asserts. They are DECISIONS, not measurements:
# each was chosen well inside the margin the measurement left, so that a
# slower or faster machine still clears it. If one of these ever fails, the
# claim on the page has stopped being true and the build should say so.
RAISE_FLOOR = 2  # raising costs at least this many times not raising
TRY_CEILING = 1.25  # a try that does not fire, against the check


def main() -> int:
    rates = RATES

    counts = {
        ("plain", "happy"): executed(plain, rates, "GBP"),
        ("lbyl", "happy"): executed(lbyl, rates, "GBP"),
        ("eafp", "happy"): executed(eafp, rates, "GBP"),
        ("plain", "unhappy"): executed(plain, rates, "ZZZ"),
        ("lbyl", "unhappy"): executed(lbyl, rates, "ZZZ"),
        ("eafp", "unhappy"): executed(eafp, rates, "ZZZ"),
    }
    for (shape, path), n in counts.items():
        print(f"  {shape:6} {path:8} {n:3} instructions")

    table = len(eafp.__code__.co_exceptiontable)
    print(f"  eafp exception table: {table} bytes; "
          f"lbyl: {len(lbyl.__code__.co_exceptiontable)}")

    # The chapter's prose says "one instruction", in words, beside this
    # value, and prose cannot be a \val{}. So the claim is asserted here: a
    # CPython that changes the count fails the build rather than putting
    # "adds 2 instruction" on the page with nothing able to see it.
    overhead = counts[("eafp", "happy")] - counts[("plain", "happy")]
    assert overhead == 1, (
        f"a try adds {overhead} instructions on the happy path; the chapter "
        f"says one, in words"
    )
    assert not lbyl.__code__.co_exceptiontable, "lbyl compiles no handler"
    assert table > 0, "eafp compiles its handler into the exception table"

    timings = {
        ("lbyl", "happy"): nanoseconds('lbyl(RATES, "GBP")'),
        ("eafp", "happy"): nanoseconds('eafp(RATES, "GBP")'),
        ("lbyl", "unhappy"): nanoseconds('lbyl(RATES, "ZZZ")'),
        ("eafp", "unhappy"): nanoseconds('eafp(RATES, "ZZZ")'),
    }
    for (shape, path), t in timings.items():
        print(f"  {shape:6} {path:8} {t * 1e9:8.1f} ns  (this machine only)")

    raised = timings[("eafp", "unhappy")] / timings[("eafp", "happy")]
    against_check = timings[("eafp", "happy")] / timings[("lbyl", "happy")]
    print(f"  raising costs {raised:.1f}x not raising "
          f"(asserted floor: {RAISE_FLOOR})")
    print(f"  a try that does not fire costs {against_check:.2f}x the check "
          f"(asserted ceiling: {TRY_CEILING})")
    assert raised >= RAISE_FLOOR, (
        f"raising cost only {raised:.1f}x not raising, under the floor of "
        f"{RAISE_FLOOR} this book prints"
    )
    assert against_check <= TRY_CEILING, (
        f"a try that does not fire cost {against_check:.2f}x the check, over "
        f"the ceiling of {TRY_CEILING} this book prints"
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        "% Generated by code/measure/e03_try_cost.py -- do not edit.\n"
        "% Instruction counts are exact and reproducible on the pinned\n"
        "% interpreter. The two ratios are BOUNDS the script asserts, not\n"
        "% timings: a timing is a property of the machine that ran it.\n"
        + "".join(
            f"\\pyval{{e03.{shape}.{path}}}{{{n}}}\n"
            for (shape, path), n in counts.items()
        )
        + f"\\pyval{{e03.try.overhead}}{{{overhead}}}\n"
        + f"\\pyval{{e03.exctable}}{{{table}}}\n"
        + f"\\pyval{{e03.raise.floor}}{{{RAISE_FLOOR}}}\n"
        + f"\\pyval{{e03.try.ceiling}}{{{TRY_CEILING}}}\n",
        encoding="utf8",
    )
    print(f"  wrote {OUT.relative_to(OUT.parents[2])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
