"""Run pytest over one file, for the two exercises about test SHAPE.

Exercises 11.1 and 11.2 ask you to restructure a test file rather than to
implement a function, so their checks have to run your tests and then look
at how you wrote them. Both things are done here, and neither reaches into
pytest's internals: `_run` is the public command line, and `source` is the
file you edited.

The leading underscore keeps this out of pytest's collection and out of the
book's listing ledger. It is harness, not chapter content.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType

CODE = Path(__file__).resolve().parents[2]
# The same three the transcript writer pins, for the same reason: pytest
# sizes its rules to the terminal, and it prints a longer assertion diff
# when CI or BUILD_NUMBER is set. A check that reads pytest's output must
# not see one thing on your machine and another on a runner.
ENV = {**os.environ, "COLUMNS": "79", "CI": "", "BUILD_NUMBER": ""}


def run(module: ModuleType) -> subprocess.CompletedProcess[str]:
    """Run pytest over whichever file `load` gave us, starter or solution."""
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            module.__file__ or "",
            # `-o addopts=` clears the project's own `-q`. Without it the
            # two quiet flags stack into -qq, which drops the "4 passed"
            # summary line an exercise below reads.
            "-o",
            "addopts=",
            "-q",
            "--no-header",
            "-p",
            "no:cacheprovider",
        ],
        cwd=CODE,
        capture_output=True,
        text=True,
        env=ENV,
        check=False,
    )


def source(module: ModuleType) -> str:
    """The text of the file you edited."""
    return Path(module.__file__ or "").read_text(encoding="utf8")
