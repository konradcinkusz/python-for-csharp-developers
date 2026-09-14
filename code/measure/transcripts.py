#!/usr/bin/env python3
"""Run the listings whose output the book quotes, and write the transcripts.

A transcript typed into a chapter is one that cannot quote a computed value
and that nobody can tell from one that was never run. So every quoted output
is a file under figures/transcripts/, written here by running the listing on
the pinned interpreter, and pulled onto the page with \\transcript{stem}.

Three guards, and each was watched failing before it was believed:

  * ASCII only. The transcript goes through `listings`, which aborts the
    build on a multi-byte character it has no literate mapping for.
  * No control characters. `ord(ch) > 127` alone lets an ESC byte (an ANSI
    colour code) or a raw tab through -- both are under 128 and both are
    real: a library that colours its output writes ESC, and `listings`
    prints an ANSI sequence as visible mojibake rather than colour, or
    expands a tab past the 79-column budget the width check below has
    already cleared it against. Reproduced with a two-line probe carrying
    "\x1b[31m" and a literal tab; the old guard passed both.
  * 79 columns. `listings` is set to wrap a long line silently, printing an
    arrow into the middle of what the reader is meant to paste back into a
    terminal; zero overfull boxes is not evidence that anything fits.

Run from code/:   uv run python measure/transcripts.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CODE = Path(__file__).resolve().parents[1]
OUT = CODE.parent / "figures" / "transcripts"
WIDTH = 79

# stem -> the listing whose stdout it is, relative to code/
#
# Only a listing whose output the book QUOTES belongs here. ch08/one_loop.py
# is deliberately absent: it prints milliseconds, which differ on every
# machine, so the chapter quotes E4's bounds instead and tells the reader to
# run that listing themselves.
TRANSCRIPTS = {
    "ch00-loop": "ch00/loop.py",
    "ch03-hint-is-a-claim": "ch03/hint_is_a_claim.py",
    "ch03-dto-four-ways": "ch03/dto_four_ways.py",
    "ch03-defaults": "ch03/defaults.py",
    "ch06-chaining": "ch06/chaining.py",
    "ch06-swallow": "ch06/swallow.py",
    "ch06-groups": "ch06/groups.py",
    "ch07-runs-once": "ch07/runs_once.py",
    "ch07-two-ways": "ch07/two_ways.py",
    "ch07-shadowing": "ch07/shadowing.py",
    "ch07-cycles": "ch07/cycles.py",
    "ch08-boundary": "ch08/boundary.py",
    "ch08-cancelled": "ch08/cancelled.py",
    "ch08-cold": "ch08/cold.py",
    "ch08-deadline": "ch08/deadline.py",
    "ch08-whenall": "ch08/whenall.py",
    "ch10-async": "ch10/async_session.py",
    "ch10-autogenerate": "ch10/autogenerate.py",
    "ch10-expiry": "ch10/expiry.py",
    "ch10-frames": "ch10/frames.py",
    "ch10-nplusone": "ch10/nplusone.py",
    "ch12-logging-default": "ch12/logging_default.py",
    "ch12-log-setup": "ch12/log_setup.py",
    "ch12-correlation": "ch12/correlation.py",
    "ch12-shutdown": "ch12/shutdown.py",
}


def run(listing: str) -> str:
    result = subprocess.run(
        [sys.executable, listing],
        cwd=CODE,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


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


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for stem, listing in TRANSCRIPTS.items():
        text = run(listing)
        guard(stem, text)
        (OUT / f"{stem}.txt").write_text(text, encoding="utf8")
        print(f"  {stem}: {len(text.splitlines())} line(s) from {listing}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
