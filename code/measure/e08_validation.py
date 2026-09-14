#!/usr/bin/env python3
"""E8 -- what one structured output costs to validate, and what it buys.

The experiment chapter 13's brief asks for: pydantic strict, pydantic lax
and a dataclass over `json`, on one structured output. It answers two
questions, and only one of them is about speed.

The corpus and the three strategies are IMPORTED from the listing the
chapter prints, ch13/what_survives.py, rather than copied here. A second
copy of a corpus is the next thing to go stale, and then the table on the
page is measuring something the experiment is not.

WHAT IS COMMITTED, AND WHY NONE OF IT IS A TIMING. `make verify` re-runs
this script and fails on any byte that moved, so a microsecond figure
written here would fail on the next machine -- which would be the right
answer for the wrong reason, because the figure was never reproducible in
the first place. The trilogy's rule is that a machine-dependent residual is
committed as a BOUND, never as a figure, and a bound is a decision the
script checks rather than an observation it records. So this file commits:

  * exact counts -- how many malformed replies each strategy lets past.
    Those are properties of the code and identical on every machine.
  * two bounds, written here as constants and asserted on every run. If a
    later pydantic makes strict expensive, or stops beating the standard
    library's parser, CI fails and the chapter is wrong the same day.

Run from code/:   uv run python measure/e08_validation.py
"""

from __future__ import annotations

import json
import sys
import timeit
from pathlib import Path

CODE = Path(__file__).resolve().parents[1]
# The listing is the source of truth for the corpus, so this script has to
# be able to import it the way the reader runs it: from inside ch13/.
sys.path.insert(0, str(CODE / "ch13"))

from what_survives import MALFORMED, STRATEGIES, rejects  # noqa: E402

OUT = CODE.parent / "figures" / "values"

# The two bounds. DECISIONS, generously sized, checked every run -- not
# measurements. On the machine this was written on, strict came out within
# a few per cent of lax (either side of it, run to run) and pydantic beat
# json.loads by 2.7x; the constants leave a slower or busier machine room
# to agree without the page having to change.
STRICT_OVERHEAD_PCT = 50   # strict costs at most this much more than lax
JSON_FACTOR = 2            # json.loads ALONE is at least this much slower

ITERATIONS = 20_000
REPEATS = 5

SMALL = json.dumps(
    {"summary": "disk full", "severity": 2, "needs_human": False}
)
# A realistic reply: the three fields that matter, and thirty the provider
# also sent. Both strategies have to get through all of it.
WIDE = json.dumps(
    {
        "summary": "disk full",
        "severity": 2,
        "needs_human": False,
        **{f"extra_{i}": f"value-{i}" for i in range(30)},
    }
)


def fastest(stmt: str, env: dict[str, object]) -> float:
    """Seconds per call, best of REPEATS.

    The minimum, not the mean: the fastest run is the one least disturbed
    by the scheduler, where an average is an average of the disturbances.
    """
    runs = timeit.Timer(stmt, globals=env).repeat(
        repeat=REPEATS, number=ITERATIONS
    )
    return min(runs) / ITERATIONS


def main() -> int:
    counts = {
        name: sum(rejects(strategy, raw) for _, raw in MALFORMED)
        for name, strategy in STRATEGIES.items()
    }

    env: dict[str, object] = {
        "lax": STRATEGIES["lax"],
        "strict": STRATEGIES["strict"],
        "json": json,
        "SMALL": SMALL,
        "WIDE": WIDE,
    }
    lax_small = fastest("lax(SMALL)", env)
    strict_small = fastest("strict(SMALL)", env)
    lax_wide = fastest("lax(WIDE)", env)
    json_wide = fastest("json.loads(WIDE)", env)

    overhead_pct = (strict_small / lax_small - 1) * 100
    factor = json_wide / lax_wide

    # The assertions ARE the experiment. A bound nothing checks is a
    # sentence, and this book does not print sentences as measurements.
    assert overhead_pct <= STRICT_OVERHEAD_PCT, (
        f"strict cost {overhead_pct:.0f}% more than lax, over the "
        f"{STRICT_OVERHEAD_PCT}% this chapter commits to"
    )
    assert factor >= JSON_FACTOR, (
        f"json.loads alone was only {factor:.2f}x pydantic's whole "
        f"parse-and-validate, under the {JSON_FACTOR}x committed"
    )
    assert counts["strict"] > counts["lax"] > counts["plain"], (
        f"the ordering this chapter rests on no longer holds: {counts}"
    )

    values = {
        "e08.corpus": len(MALFORMED),
        "e08.reject.lax": counts["lax"],
        "e08.reject.strict": counts["strict"],
        "e08.reject.plain": counts["plain"],
        "e08.silent.plain": len(MALFORMED) - counts["plain"],
        "e08.fields.wide": len(json.loads(WIDE)),
        "e08.strict.overhead.pct": STRICT_OVERHEAD_PCT,
        "e08.json.factor": JSON_FACTOR,
        "e08.iterations": ITERATIONS,
        "e08.repeats": REPEATS,
    }

    lines = [
        "% Generated by code/measure/e08_validation.py --- do not edit."
    ]
    lines += [f"\\pyval{{{k}}}{{{v}}}" for k, v in values.items()]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "e08.tex").write_text("\n".join(lines) + "\n", encoding="utf8")

    print(f"  e08: rejected of {len(MALFORMED)}: " + ", ".join(
        f"{n}={c}" for n, c in counts.items()))
    print(f"  e08: strict overhead {overhead_pct:+.0f}% "
          f"(ceiling {STRICT_OVERHEAD_PCT}%)")
    print(f"  e08: json.loads alone {factor:.2f}x lax on "
          f"{len(json.loads(WIDE))} fields (floor {JSON_FACTOR}x)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
