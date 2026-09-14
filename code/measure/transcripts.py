#!/usr/bin/env python3
"""Run the listings whose output the book quotes, and write the transcripts.

A transcript typed into a chapter is one that cannot quote a computed value
and that nobody can tell from one that was never run. So every quoted output
is a file under figures/transcripts/, written here by running the listing on
the pinned interpreter, and pulled onto the page with \\transcript{stem}.

Two shapes of transcript, because chapter 11 needs the second:

  * A LISTING's stdout -- `Listing("ch00/loop.py")` -- which is the original
    case and stays the common one.
  * A COMMAND's output -- `Command([...])` -- for a transcript that is the
    output of a tool rather than of a script: a pytest report, a coverage
    table. The chapter about testing cannot show what a failure looks like
    without running a failure, and a failing listing is not something
    tests/test_listings.py can be asked to tolerate.

A command transcript must be REPRODUCIBLE, and pytest's default output is
not: the header carries an absolute rootdir, the footer carries an elapsed
time, and a traceback that displays a fixture argument or a `module.attr`
callable carries a memory address. Every one of those differs between this
machine and CI, and `make verify` would then fail on every run for reasons
that are not defects. So the commands below pass `-q --no-header`, the
`extract` slice keeps only the report between two stable markers, and the
files under ch11/ were written to avoid the two address-bearing forms --
measured by running each twice and diffing, not by reasoning about it.

Three guards, and each was watched failing before it was believed:

  * ASCII only. The transcript goes through `listings`, which aborts the
    build on a multi-byte character it has no literate mapping for.
  * No control characters. `ord(ch) > 127` alone lets an ESC byte (an ANSI
    colour code) or a raw tab through -- both are under 128 and both are
    real: a library that colours its output writes ESC, and `listings`
    prints an ANSI sequence as visible mojibake rather than colour, or
    expands a tab past the 79-column budget the width check below has
    already cleared it against.
  * 79 columns. `listings` is set to wrap a long line silently, printing an
    arrow into the middle of what the reader is meant to paste back into a
    terminal; zero overfull boxes is not evidence that anything fits.

Run from code/:   uv run python measure/transcripts.py
"""

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

CODE = Path(__file__).resolve().parents[1]
OUT = CODE.parent / "figures" / "transcripts"
WIDTH = 79

# pytest and coverage size their rules to the terminal, and fall back to
# 80 when there is no tty -- one column over the budget, and a number that
# is a property of whatever ran the build rather than of the book. Pinned
# here so the transcript is the same on this machine and on CI.
ENV = {**os.environ, "COLUMNS": str(WIDTH)}


@dataclass(frozen=True)
class Listing:
    """A listing file, run as a script. Its stdout is the transcript."""

    path: str


@dataclass(frozen=True)
class Command:
    """A command, run from code/. Optionally sliced to a stable region.

    `start` and `end` are matched as substrings against whole lines. The
    slice keeps the start line and drops the end line, which is how the
    volatile "N failed in 0.13s" footer is left out of a pytest report
    without pretending it was never printed.
    """

    argv: list[str]
    start: str | None = None
    end: str | None = None
    expect: int | None = None


# stem -> the Listing whose stdout it is, or the Command whose report it is.
#
# Only something whose output the book QUOTES belongs here. ch08/one_loop.py
# is deliberately absent: it prints milliseconds, which differ on every
# machine, so the chapter quotes E4's bounds instead and tells the reader to
# run that listing themselves.
TRANSCRIPTS: dict[str, Listing | Command] = {
    "ch00-loop": Listing("ch00/loop.py"),
    "ch03-hint-is-a-claim": Listing("ch03/hint_is_a_claim.py"),
    "ch03-dto-four-ways": Listing("ch03/dto_four_ways.py"),
    "ch03-defaults": Listing("ch03/defaults.py"),
    "ch06-chaining": Listing("ch06/chaining.py"),
    "ch06-swallow": Listing("ch06/swallow.py"),
    "ch06-groups": Listing("ch06/groups.py"),
    "ch07-runs-once": Listing("ch07/runs_once.py"),
    "ch07-two-ways": Listing("ch07/two_ways.py"),
    "ch07-shadowing": Listing("ch07/shadowing.py"),
    "ch07-cycles": Listing("ch07/cycles.py"),
    "ch08-cold": Listing("ch08/cold.py"),
    "ch08-whenall": Listing("ch08/whenall.py"),
    "ch08-cancelled": Listing("ch08/cancelled.py"),
    "ch08-deadline": Listing("ch08/deadline.py"),
    "ch08-boundary": Listing("ch08/boundary.py"),
    "ch10-async": Listing("ch10/async_session.py"),
    "ch10-autogenerate": Listing("ch10/autogenerate.py"),
    "ch10-expiry": Listing("ch10/expiry.py"),
    "ch10-frames": Listing("ch10/frames.py"),
    "ch10-nplusone": Listing("ch10/nplusone.py"),
    # Chapter 11. Each of the two pytest runs is a FAILING run on purpose:
    # the file it names is a trap_*.py, which the suite never collects
    # because the name does not begin with test_.
    "ch11-assert-rewrite": Command(
        argv=[
            sys.executable, "-m", "pytest", "ch11/trap_assert.py",
            "-q", "--no-header", "-p", "no:cacheprovider",
        ],
        start="FAILURES",
        end="short test summary",
        expect=1,
    ),
    "ch11-patch-trap": Command(
        argv=[
            sys.executable, "-m", "pytest", "ch11/trap_patch.py",
            "-q", "--no-header", "-p", "no:cacheprovider",
        ],
        start="FAILURES",
        end="short test summary",
        expect=1,
    ),
    # Coverage over a test that runs every line of pricing.py and checks
    # almost nothing. The report is the chapter's point, not its evidence
    # of quality.
    "ch11-coverage": Command(
        argv=[sys.executable, "-m", "coverage", "report", "-m"],
    ),
}

# Run before the transcript above it, because `coverage report` reads a data
# file that `coverage run` has to have written first. Keeping it out of
# TRANSCRIPTS keeps that dict a list of things the book prints.
PRELUDE: list[list[str]] = [
    [
        sys.executable, "-m", "coverage", "run", "--source=pricing",
        "-m", "pytest", "ch11/trap_coverage.py",
        "-q", "--no-header", "-p", "no:cacheprovider",
    ],
]


def run_listing(listing: str) -> str:
    result = subprocess.run(
        [sys.executable, listing],
        cwd=CODE,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def run_command(spec: Command) -> str:
    result = subprocess.run(
        spec.argv,
        cwd=CODE,
        capture_output=True,
        text=True,
        check=False,
        env=ENV,
    )
    if spec.expect is not None and result.returncode != spec.expect:
        raise SystemExit(
            f"{' '.join(spec.argv)} exited {result.returncode}, "
            f"expected {spec.expect}. A transcript of a failure that "
            f"stopped failing is a transcript of nothing.\n"
            f"--- stdout ---\n{result.stdout}"
            f"--- stderr ---\n{result.stderr}"
        )
    return slice_output(result.stdout, spec)


def slice_output(text: str, spec: Command) -> str:
    if spec.start is None:
        return text
    lines = text.splitlines()
    try:
        first = next(
            i for i, ln in enumerate(lines) if spec.start in ln
        )
    except StopIteration:
        raise SystemExit(
            f"{' '.join(spec.argv)}: no line contains {spec.start!r}; "
            f"the report's shape has changed and the slice is now "
            f"quoting something else.\n{text}"
        ) from None
    last = len(lines)
    if spec.end is not None:
        last = next(
            (i for i, ln in enumerate(lines) if i > first and spec.end in ln),
            len(lines),
        )
    return "\n".join(lines[first:last]).rstrip() + "\n"


def guard(stem: str, text: str) -> None:
    for n, line in enumerate(text.splitlines(), start=1):
        if any(ord(ch) > 127 for ch in line):
            raise SystemExit(f"{stem}: line {n} is not ASCII: {line!r}")
        if any(ord(ch) < 32 for ch in line):
            raise SystemExit(
                f"{stem}: line {n} has a control character (an ANSI "
                f"escape or a tab, most likely): {line!r}"
            )
        if len(line) > WIDTH:
            raise SystemExit(
                f"{stem}: line {n} is {len(line)} columns, over {WIDTH}: "
                f"{line!r}"
            )
        # A memory address is the reproducibility failure this file exists
        # to avoid, and it is invisible to the three guards above: it is
        # ASCII, printable and short. Caught by name instead.
        if "0x7f" in line or "0x55" in line:
            raise SystemExit(
                f"{stem}: line {n} looks like it carries a memory "
                f"address, which differs on every run and would make "
                f"`make verify` fail for no reason: {line!r}"
            )


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for argv in PRELUDE:
        subprocess.run(
            argv, cwd=CODE, capture_output=True, check=False, env=ENV
        )
    for stem, spec in TRANSCRIPTS.items():
        if isinstance(spec, Listing):
            text = run_listing(spec.path)
            source = spec.path
        else:
            text = run_command(spec)
            source = " ".join(Path(a).name for a in spec.argv[1:4])
        guard(stem, text)
        (OUT / f"{stem}.txt").write_text(text, encoding="utf8")
        print(f"  {stem}: {len(text.splitlines())} line(s) from {source}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
