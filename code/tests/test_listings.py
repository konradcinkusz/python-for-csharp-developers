"""Every listing file under chNN/ runs as a script and exits cleanly.

This is the floor, not the ceiling: a listing that runs is not yet a listing
that prints what the chapter says it prints. Where a chapter quotes a
listing's output it does so through a generated transcript under
figures/transcripts/, written by measure/transcripts.py, so the quoted output
is what the pinned interpreter produced rather than what the author
remembered.
"""

from __future__ import annotations

import runpy
from pathlib import Path

import pytest

CODE = Path(__file__).resolve().parent.parent
LISTINGS = sorted(
    p
    for d in sorted(CODE.glob("ch[0-9][0-9]"))
    for p in d.glob("*.py")
    if not p.name.startswith("_")
)


def _listing_id(p: Path) -> str:
    return p.relative_to(CODE).as_posix()


@pytest.mark.parametrize("path", LISTINGS, ids=_listing_id)
def test_listing_runs(path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    runpy.run_path(str(path), run_name="__main__")
    out = capsys.readouterr()
    assert out.err == "", f"{path.name} wrote to stderr:\n{out.err}"


def test_there_is_at_least_one_listing() -> None:
    # A parametrised test over an empty list is silently skipped, and a
    # check that passes because it read nothing is worse than no check.
    assert LISTINGS, "no listing files found under code/chNN/"
