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
# pytest sizes its rules to the terminal; pinning the width keeps a failure
# message the same here and on CI, which is the same reason
# code/measure/transcripts.py pins it.
ENV = {**os.environ, "COLUMNS": "79"}


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
