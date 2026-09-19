#!/usr/bin/env python3
"""What `s += piece` in a loop actually costs, measured rather than recalled.

The folklore -- and `notes/02-traps.md` entry 23, as first written -- says
building a string with `+=` in a loop is quadratic and `"".join(...)` is
linear. On CPython the first half is false for the case people actually
write. The interpreter carries a specialisation for exactly this shape,
and it names itself: disassemble a warmed-up loop and the opcode is
BINARY_OP_INPLACE_ADD_UNICODE. When the left operand has no other
reference, the string is resized in place and the loop is linear.

It is quadratic again the moment anything else holds a reference, because
the in-place resize is then unsafe and the interpreter falls back to
allocating a new string per iteration. That is the trap worth printing:
not "+= is slow", but "+= is fast until an unrelated line elsewhere makes
it slow, silently".

TIMINGS ARE NOT COMMITTED AS FIGURES. A duration is a property of the
machine, so what reaches the page is a BOUND the measurement clears -- the
rule notes/01-curriculum.md sets for a machine-dependent residual -- and
`make verify` stays reproducible because a bound is a decision rather than
an observation.

Two things this measures the hard way, both after a first version failed on
a loaded machine and reported the linear loop doubling by a factor of four:

  * Each variant is timed at a size where one run takes tens of
    milliseconds, not tenths. The first version ran the linear loops for a
    sixth of a millisecond, which is inside the scheduler's noise.
  * The small and the large run are INTERLEAVED inside one trial and the
    ratio is taken per trial, then the median over trials. A contention
    episode then lands on both halves of one ratio rather than on one side
    of a min-over-trials, which is what made the first version flip.

The linear and the quadratic variants are timed at different sizes on
purpose: the quadratic one at the linear one's size would run for minutes,
which is the point being measured.

Run from code/:   uv run python measure/ch05_concat.py
"""

from __future__ import annotations

import dis
import statistics
import sys
import time
from collections.abc import Callable
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "figures" / "values"

LINEAR_SMALL = 400_000
LINEAR_LARGE = 800_000
QUAD_SMALL = 3_000
QUAD_LARGE = 6_000
TRIALS = 9
PIECE = "x" * 10

# The two bounds. Chosen with room for a loaded machine, not fitted to a
# run: a doubling of n multiplies linear work by 2 and quadratic work by 4,
# and these sit either side of the gap with most of it to spare.
LINEAR_UNDER = 2.5
QUADRATIC_OVER = 3.0


def concat_plain(n: int) -> int:
    """The loop everybody writes: one local, nothing else holding it."""
    s = ""
    for _ in range(n):
        s += PIECE
    return len(s)


def concat_shared(n: int) -> int:
    """The same loop, with one more reference to the string alive."""
    history: list[str] = []
    s = ""
    for _ in range(n):
        history.append(s)
        s += PIECE
    return len(s)


def concat_join(n: int) -> int:
    return len("".join(PIECE for _ in range(n)))


def once(fn: Callable[[int], int], n: int) -> float:
    start = time.perf_counter()
    fn(n)
    return time.perf_counter() - start


def ratio(fn: Callable[[int], int], name: str, small: int, large: int
          ) -> float:
    """Median of TRIALS interleaved small/large ratios."""
    ratios: list[float] = []
    for _ in range(TRIALS):
        a = once(fn, small)
        b = once(fn, large)
        ratios.append(b / a)
    median = statistics.median(ratios)
    print(f"  {name:14} n {small} -> {large}   x{median:.2f}"
          f"   (spread x{min(ratios):.2f} to x{max(ratios):.2f})")
    return median


def specialised_opcode() -> str:
    """Ask the interpreter what it did, rather than writing it down."""
    concat_plain(500)  # warm the loop so the adaptive form settles
    names = {
        instruction.opname
        for instruction in dis.get_instructions(concat_plain, adaptive=True)
        if "ADD" in instruction.opname
    }
    if len(names) != 1:
        raise SystemExit(f"expected one add opcode, saw {sorted(names)}")
    return names.pop()


def main() -> int:
    opcode = specialised_opcode()
    print(f"  specialised opcode: {opcode}")
    plain = ratio(concat_plain, "+= plain", LINEAR_SMALL, LINEAR_LARGE)
    join = ratio(concat_join, "join", LINEAR_SMALL, LINEAR_LARGE)
    shared = ratio(concat_shared, "+= shared", QUAD_SMALL, QUAD_LARGE)

    if plain >= LINEAR_UNDER:
        raise SystemExit(f"+= plain doubled by x{plain:.2f}, not under "
                         f"{LINEAR_UNDER}: the in-place path did not apply")
    if join >= LINEAR_UNDER:
        raise SystemExit(f"join doubled by x{join:.2f}, not under "
                         f"{LINEAR_UNDER}")
    if shared <= QUADRATIC_OVER:
        raise SystemExit(f"+= shared doubled by x{shared:.2f}, not over "
                         f"{QUADRATIC_OVER}: expected quadratic growth")
    # The bounds above are absolute and a loaded machine moves both
    # medians the same way; this one is a comparison, so it survives
    # contention that would move either bound on its own.
    if shared <= plain * 1.5:
        raise SystemExit(f"+= shared (x{shared:.2f}) is not clear of "
                         f"+= plain (x{plain:.2f}); the two shapes did "
                         f"not separate")

    lines = [
        "% Generated by code/measure/ch05_concat.py --- do not edit.",
        # The value file is LaTeX, so the underscores in an opcode name
        # are escaped here rather than on the page: an unescaped one is a
        # subscript, which is the single most common way to break this
        # build.
        f"\\pyvaltext{{ch05.concat.opcode}}"
        f"{{{opcode.replace('_', chr(92) + '_')}}}",
        f"\\pyval{{ch05.concat.small}}{{{LINEAR_SMALL}}}",
        f"\\pyval{{ch05.concat.large}}{{{LINEAR_LARGE}}}",
        f"\\pyval{{ch05.concat.qsmall}}{{{QUAD_SMALL}}}",
        f"\\pyval{{ch05.concat.qlarge}}{{{QUAD_LARGE}}}",
        f"\\pyval{{ch05.concat.linear}}{{{LINEAR_UNDER}}}",
        f"\\pyval{{ch05.concat.quadratic}}{{{QUADRATIC_OVER}}}",
    ]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "ch05_concat.tex").write_text("\n".join(lines) + "\n",
                                         encoding="utf8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
