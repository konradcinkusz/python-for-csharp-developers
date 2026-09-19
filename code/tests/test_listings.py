"""Every listing file under chNN/ runs as a script and exits cleanly.

This is the floor, not the ceiling: a listing that runs is not yet a listing
that prints what the chapter says it prints. Where a chapter quotes a
listing's output it does so through a generated transcript under
figures/transcripts/, written by measure/transcripts.py, so the quoted output
is what the pinned interpreter produced rather than what the author
remembered.

A REAL SUBPROCESS, not runpy.run_path in-process. The front matter tells the
reader to run a listing as `uv run python chNN/file.py`, from code/, and a
subprocess is what makes that claim checked rather than merely similar. It
also settles `sys.exit(main())`, the ordinary idiom for a script with a
return code: run in-process via runpy, that raises SystemExit(0) into pytest
itself, which reports it as a FAILURE -- a listing that exits 0 as intended
was failing the one test whose job is to prove it runs. Reproduced on a
throwaway `ch01/exits.py` ending `sys.exit(main())` with `main()` returning
0: in-process, `SystemExit: 0`, FAILED; as a subprocess, exit code 0, passed.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

CODE = Path(__file__).resolve().parent.parent
LISTINGS = sorted(
    p
    for d in sorted(CODE.glob("ch[0-9][0-9]"))
    # rglob, not glob: a chapter's own subdirectory (a small package a
    # listing imports from, say) is real chapter content and \pyfile can
    # point at any path under it. A flat glob("*.py") silently ran and
    # counted only the top level, so a nested file could sit on the page
    # with no verifybox and never actually run.
    for p in d.rglob("*.py")
    if not p.name.startswith("_")
)


def _listing_id(p: Path) -> str:
    return p.relative_to(CODE).as_posix()


@pytest.mark.parametrize("path", LISTINGS, ids=_listing_id)
def test_listing_runs(path: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(path.relative_to(CODE))],
        cwd=CODE,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"{path.name} exited {result.returncode}\n"
        f"--- stdout ---\n{result.stdout}"
        f"--- stderr ---\n{result.stderr}"
    )
    assert result.stderr == "", (
        f"{path.name} wrote to stderr:\n{result.stderr}"
    )


def test_there_is_at_least_one_listing() -> None:
    # A parametrised test over an empty list is silently skipped, and a
    # check that passes because it read nothing is worse than no check.
    assert LISTINGS, "no listing files found under code/chNN/"
