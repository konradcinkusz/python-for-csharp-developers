#!/usr/bin/env python3
"""Run the listings whose output the book quotes, and write the transcripts.

A transcript typed into a chapter is one that cannot quote a computed value
and that nobody can tell from one that was never run. So every quoted output
is a file under figures/transcripts/, written here by running the listing on
the pinned interpreter, and pulled onto the page with \\transcript{stem}.

Two guards, and both were watched failing before they were believed:

  * ASCII only. The transcript goes through `listings`, which aborts the
    build on a multi-byte character it has no literate mapping for.
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
TRANSCRIPTS = {
    "ch00-loop": "ch00/loop.py",
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
