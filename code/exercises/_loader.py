"""Load an exercise module from the reader's starter or from the solution.

Every exercise is two files: the starter the reader edits and the reference
solution under solutions/. A test imports the module through here rather than
with a plain import, so the SAME test runs against whichever of the two the
environment names:

    uv run pytest -k e00_01                   # the starter -- the reader
    PYBOOK_SOLUTIONS=1 uv run pytest          # the solutions -- CI

The starter is expected to FAIL its test: an exercise whose starter already
passes is not an exercise. The build checks that too, with
PYBOOK_STARTERS=fail, under which conftest.py marks every exercise test as a
strict expected failure.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from types import ModuleType

HERE = Path(__file__).resolve().parent


def load(chapter: str, key: str) -> ModuleType:
    """Import exercises/<chapter>/<key>.py, or its solution under CI."""
    folder = HERE / chapter
    # A truthiness test on the raw string reads PYBOOK_SOLUTIONS=0 as ON,
    # because "0" is a non-empty string -- an exported but explicitly-off
    # variable would then silently run the solutions rather than the
    # starter. Off is unset, empty, or "0"; anything else (documented as
    # "1") is on.
    if os.environ.get("PYBOOK_SOLUTIONS", "0") not in ("0", ""):
        folder = folder / "solutions"
    path = folder / f"{key}.py"
    spec = importlib.util.spec_from_file_location(f"exercise_{key}", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load exercise from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module
