#!/usr/bin/env python3
"""Experiment E1: what the global interpreter lock costs, and what removing
it costs instead.

Four threads, three workloads, two interpreters -- the default 3.14 build and
the free-threaded `python3.14t` -- with the workloads imported from
ch01/workloads.py rather than copied, so the numbers the book prints came out
of the listing the reader runs.

TWO MODES, and the split is forced rather than tidy. Every other script under
measure/ is deterministic: it counts the tree, or it runs a listing whose
output is fixed. A TIMING is not. CI re-runs every script here on every push
and fails the build when a committed value moves, so a script that measured
wall time on each run could never be green on two machines -- and a wall time
that survived that gate would have to have been rounded until it said
nothing. So:

    uv run python measure/e01_gil.py --record   # measures; writes the JSON
    uv run python measure/e01_gil.py            # reads the JSON; writes .tex

The JSON under measure/data/ is the experiment's raw result, committed, with
the machine and both interpreters recorded beside it. `make numbers` runs the
second mode only, which is a pure function of that file, so the drift gate
still asks a question it can answer: does the page agree with the measurement
that was taken? Re-recording is a deliberate act, and it shows up in review as
a diff of the data rather than of the prose.

The ratios are what the chapter argues from and they are structural: four
threads of pure-Python work take four times as long as one, on any machine
with four cores, because the lock says so. The absolute times are a property
of the machine named in the JSON and the chapter says so.
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import statistics
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import TypedDict, cast

CODE = Path(__file__).resolve().parents[1]
ROOT = CODE.parent
DATA = CODE / "measure" / "data" / "e01.json"
OUT = ROOT / "figures" / "values" / "e01.tex"

# Repeats of the whole listing, on top of the median the listing takes over
# its own trials. The listing is left exactly as the reader runs it; the
# statistical weight is added here, in the harness, so that "the book's
# numbers came out of that file" stays literally true.
REPEATS = 7

# The driver runs inside each interpreter and prints one JSON line, so
# nothing here parses a formatted table. Rows come back as a mapping of
# workload name to [one thread, four threads] rather than as the listing's
# own tuples, because a list of mixed types is a list of Unknown to a strict
# checker and this project runs one.
DRIVER = (
    "import json, sys; sys.path.insert(0, 'ch01');"
    " import interpreter, workloads;"
    " print(json.dumps({'facts': interpreter.facts(),"
    " 'rows': {n: [a, b] for n, a, b in workloads.measure()}}))"
)


class RunResult(TypedDict):
    """One invocation of the driver, inside one interpreter."""

    facts: list[list[str]]
    rows: dict[str, list[float]]


class Row(TypedDict):
    """One workload on one build: medians, and the spread of the ratio."""

    one: float
    many: float
    ratio_lo: float
    ratio_hi: float


class Build(TypedDict):
    version: str
    facts: dict[str, str]
    rows: dict[str, Row]


class Recorded(TypedDict):
    recorded: str
    machine: str
    repeats: int
    builds: dict[str, Build]


def freethreaded_interpreter() -> str | None:
    """The `python3.14t` binary, if this machine has one."""
    return shutil.which("python3.14t")


def run_once(executable: str) -> RunResult:
    result = subprocess.run(
        [executable, "-c", DRIVER],
        cwd=CODE,
        capture_output=True,
        text=True,
        check=True,
    )
    return cast(RunResult, json.loads(result.stdout))


def describe(executable: str) -> str:
    """Version and ABI flags: the two builds share the first and differ in
    the second, which is exactly the chapter's point and is why recording
    the version alone would have said "3.14.7" twice."""
    probe = "import sys; print(sys.version.split()[0] + sys.abiflags)"
    out = subprocess.run(
        [executable, "-c", probe],
        capture_output=True,
        text=True,
        check=True,
    )
    return out.stdout.strip()


def summarise(runs: list[RunResult]) -> dict[str, Row]:
    """Median one- and four-thread times, and how far the ratio wandered."""
    rows: dict[str, Row] = {}
    for label in runs[0]["rows"]:
        ones = [run["rows"][label][0] for run in runs]
        manys = [run["rows"][label][1] for run in runs]
        # The spread of the per-repeat ratios is kept as well as the median.
        # On four cores the lock makes the default build's numbers very
        # steady and the free-threaded build's the least steady in the
        # experiment -- because that is the only row where all four cores
        # are actually busy, so any other load on the machine lands in it.
        # A median that hid that would be a figure pretending to be an
        # invariant.
        ratios = sorted(m / o for o, m in zip(ones, manys, strict=True))
        rows[label] = {
            "one": statistics.median(ones),
            "many": statistics.median(manys),
            "ratio_lo": ratios[0],
            "ratio_hi": ratios[-1],
        }
    return rows


def record() -> int:
    """Measure on both builds and write measure/data/e01.json."""
    freethreaded = freethreaded_interpreter()
    if freethreaded is None:
        print(
            "No python3.14t on PATH: E1 needs both builds.\n"
            "  uv python install 3.14.7+freethreaded",
            file=sys.stderr,
        )
        return 1
    builds = {"default": sys.executable, "freethreaded": freethreaded}

    measured: dict[str, Build] = {}
    for name, executable in builds.items():
        runs = [run_once(executable) for _ in range(REPEATS)]
        rows = summarise(runs)
        # ch01/interpreter.py's own answers, captured under each build. The
        # free-threaded column of the chapter's table has to come from
        # somewhere, and it cannot come from a transcript: transcripts.py
        # runs a listing under sys.executable, and CI has no python3.14t.
        measured[name] = {
            "version": describe(executable),
            "facts": {pair[0]: pair[1] for pair in runs[0]["facts"]},
            "rows": rows,
        }
        print(f"  {name}: {describe(executable)}")
        for label, times in rows.items():
            ratio = times["many"] / times["one"]
            print(
                f"    {label:22} {times['one']:.3f}s -> "
                f"{times['many']:.3f}s  ({ratio:.2f}x)"
            )

    payload: Recorded = {
        "recorded": datetime.now(UTC).strftime("%Y-%m-%d"),
        "machine": (
            f"{platform.system()} {platform.machine()}, "
            f"{os.cpu_count() or 0} cores"
        ),
        "repeats": REPEATS,
        "builds": measured,
    }
    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf8"
    )
    print(f"  wrote {DATA.relative_to(ROOT)}")
    return 0


def fmt(value: float, places: int) -> str:
    return f"{value:.{places}f}"


# A \pyvaltext body reaches the page as LaTeX, so a script that writes one
# owes it the same escaping a chapter owes. This is not hypothetical: the
# first build of chapter 1 died on four "Missing $ inserted" errors and two
# overfull boxes of 98.8 and 74.7 pt, because platform.machine() on the
# commonest architecture in the world returns "x86_64" and an underscore is
# a maths subscript. Numbers go through \pyval and need none of this.
TEX_ESCAPES = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def tex(text: str) -> str:
    """Escape a string that is about to be typeset as LaTeX."""
    return "".join(TEX_ESCAPES.get(ch, ch) for ch in text)


def reproduces(one: str, many: str, ratio: str) -> bool:
    """Does the printed ratio come back out of the two printed times?

    The page shows all three, so a reader will divide. A ratio that is right
    about the measurement and wrong about the page is the defect the sibling
    books paid for six times; this is the guard, and the precision below was
    chosen by watching it fail at two decimals.
    """
    return fmt(float(many) / float(one), len(ratio.split(".")[1])) == ratio


# The five answers ch01/interpreter.py gives, under each build.
FACT_KEYS = {
    "free-threaded build": "ft",
    "GIL enabled right now": "gil",
    "JIT available / enabled": "jit",
    # No row for sys.abiflags: it is the empty string on the default build,
    # and a table cell that is deliberately blank reads as one somebody
    # forgot to fill in. The version value carries the same fact, as
    # "3.14.7" against "3.14.7t".
    "bytecode cache tag": "tag",
}

SHORT = {
    "cpu (pure Python)": "cpu",
    "io (socket read)": "io",
    "digest (C extension)": "digest",
}


def emit() -> int:
    """Read the committed measurement and write the value file."""
    if not DATA.is_file():
        print(
            f"{DATA.relative_to(ROOT)} is missing: the experiment's raw "
            f"result is committed, so this is a broken checkout rather "
            f"than a measurement that has not been taken. Re-record it "
            f"with --record.",
            file=sys.stderr,
        )
        return 1
    data = cast(Recorded, json.loads(DATA.read_text(encoding="utf8")))
    lines = [
        "% Generated by code/measure/e01_gil.py --- do not edit.",
        "% Raw measurement: code/measure/data/e01.json",
    ]

    def pyval(key: str, value: str) -> None:
        lines.append(f"\\pyval{{{key}}}{{{value}}}")

    def pyvaltext(key: str, value: str) -> None:
        lines.append(f"\\pyvaltext{{{key}}}{{{tex(value)}}}")

    pyvaltext("e01.machine", data["machine"])
    for build, payload in data["builds"].items():
        pyvaltext(f"e01.{build}.version", payload["version"])
        for label, short_key in FACT_KEYS.items():
            pyvaltext(
                f"e01.{build}.{short_key}",
                payload["facts"][label].replace("'", ""),
            )
    pyvaltext("e01.recorded", data["recorded"])
    pyval("e01.repeats", str(data["repeats"]))
    pyval("e01.threads", "4")

    cpu_times: dict[str, Row] = {}
    spreads: list[float] = []
    for build, payload in data["builds"].items():
        for label, times in payload["rows"].items():
            key = SHORT[label]
            one, many = times["one"], times["many"]
            one_s, many_s = fmt(one, 3), fmt(many, 3)
            # ONE decimal, not two. At two the guard below fired on its
            # first real run: the page would have carried 0.097, 0.398 and
            # 4.09, and the first two divide to 4.10.
            ratio_s = fmt(many / one, 1)
            # Four threads cannot genuinely finish the same per-thread
            # work sooner than one, so a printed ratio under 1.0 is not a
            # finding -- it is a measurement the machine's own noise is
            # bigger than. It happened, at a tenth of the present workload
            # size, and it would have printed "0.9" on the page.
            if float(ratio_s) < 1.0:
                print(
                    f"{build}/{key}: ratio {ratio_s} is under 1.0, which "
                    f"says four threads beat one at the same work each. "
                    f"The workload is too small for this machine: raise "
                    f"it in ch01/workloads.py and record again.",
                    file=sys.stderr,
                )
                return 1
            if not reproduces(one_s, many_s, ratio_s):
                print(
                    f"{build}/{key}: the page would print {one_s} and "
                    f"{many_s}, which divide to "
                    f"{fmt(float(many_s) / float(one_s), 1)}, not "
                    f"{ratio_s}. Drop a digit or state a bound.",
                    file=sys.stderr,
                )
                return 1
            pyval(f"e01.{build}.{key}.one", one_s)
            pyval(f"e01.{build}.{key}.many", many_s)
            pyval(f"e01.{build}.{key}.ratio", ratio_s)
            spreads.append(
                (times["ratio_hi"] - times["ratio_lo"]) / (many / one)
            )
            if key == "cpu":
                cpu_times[build] = times

    # How much any one ratio wandered across the repeats, as a percentage of
    # itself, taking the worst row. Without this the table invites a reader
    # to tell 1.0 from 1.1, which this machine cannot.
    pyval("e01.spread", fmt(max(spreads) * 100.0, 0))

    # What the free-threaded build buys on the one workload the lock
    # touches: a ratio, so it survives a change of machine, and printed to
    # one decimal so it reproduces from the two "many" columns above.
    default, freethreaded = cpu_times["default"], cpu_times["freethreaded"]
    gain = fmt(default["many"] / freethreaded["many"], 1)
    if not reproduces(
        fmt(freethreaded["many"], 3), fmt(default["many"], 3), gain
    ):
        print(
            "e01.cpu.wallclock.gain does not reproduce from the two "
            "printed times. Drop a digit or state a bound.",
            file=sys.stderr,
        )
        return 1
    pyval("e01.cpu.wallclock.gain", gain)

    # What free-threading costs a single thread, as a percentage, computed
    # from the two "one" columns so that a reader who divides them gets the
    # same answer. It is emitted as a DIFFERENCE and never as a finding:
    # across recordings it has come out at one, seven and eleven per cent
    # on this machine, all of them smaller than e01.spread, so the
    # experiment cannot separate it from the noise however confident any
    # single recording looks. The chapter says that, and quotes CPython's
    # own estimate rather than this one.
    cost = fmt((freethreaded["one"] / default["one"] - 1.0) * 100.0, 0)
    pyval("e01.cpu.singlethread.diff", cost)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf8")
    for line in lines[2:]:
        print(f"  {line}")
    return 0


def main(argv: list[str]) -> int:
    if "--record" in argv:
        return record()
    return emit()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
