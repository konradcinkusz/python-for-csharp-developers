#!/usr/bin/env python3
"""Experiment E2: cold and warm `uv sync` against `pip install -r`.

The question chapter 2 needs answered is not "is uv fast" -- everybody says
so -- but WHERE the time goes, because that is what decides whether a cache
in CI is worth configuring.

TWO MODES, and the split is the point:

    uv run python measure/e2_install.py --run    # performs the benchmark
    uv run python measure/e2_install.py          # formats the result

`--run` installs the whole dependency set repeatedly, over a real network,
and writes
measure/data/e2-install.json, which is COMMITTED. The default mode reads
that file and writes figures/values/e2.tex, and it touches no network and no
clock. That is not tidiness: `make numbers` runs every script in this
directory and the build then fails if a committed value changed, so a script
that timed something on each run would report drift on every machine it ever
ran on and the gate would have to be switched off. A timing belongs in the
tree as DATA, measured once and reviewable as a diff; only the formatting is
reproducible, and only the formatting is what CI re-runs.

METHOD, and the three things it controls for:

  * The same packages. Both tools install the export of this book's own
    uv.lock -- `uv export --no-emit-project`, hashes included -- so neither
    is resolving anything and pip is doing the least work it can be asked
    to do. `--no-install-project` keeps uv off the local package, which pip
    would have to build.
  * The same interpreter, the pinned one, for both.
  * A private cache per tool, created empty for a cold trial and reused for
    a warm one, so "cold" means cold rather than "whatever was left over".

The pip side creates its virtual environment inside the timed region, and
the uv side does too, because `uv sync` makes one -- the quantity a reader
cares about is how long it takes to get from a checkout to a runnable
environment, and with pip that includes `python -m venv`.

Reported as a median of TRIALS, with the spread, because a single run over
a network is a sample of the network. The ratios are the transferable half;
the absolute seconds are one machine on one afternoon and the chapter says
so.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

CODE = Path(__file__).resolve().parents[1]
ROOT = CODE.parent
DATA = CODE / "measure" / "data" / "e2-install.json"
OUT = ROOT / "figures" / "values" / "e2.tex"
TRIALS = 3


# --------------------------------------------------------------------------
# Running the benchmark (--run only)
# --------------------------------------------------------------------------

def _sh(args: list[str], cwd: Path, env: dict[str, str] | None = None) -> None:
    full = dict(os.environ)
    # This script runs INSIDE the book's own environment, so VIRTUAL_ENV and
    # friends are set and point at code/.venv. Left in place, uv warns that
    # the active environment is not the project's and pip installs into the
    # wrong directory -- the benchmark would then measure the wrong thing
    # while looking exactly like it worked.
    for leaked in ("VIRTUAL_ENV", "UV_PROJECT_ENVIRONMENT", "PYTHONHOME",
                   "UV_CACHE_DIR", "PIP_CACHE_DIR"):
        full.pop(leaked, None)
    # The same generous per-request ceiling for both tools. uv's default is
    # 30s and pip's 15s, and on a slow link the cold cells abort rather than
    # report -- which is a failure to measure, not a measurement. Raising it
    # for one tool only would be a thumb on the scale, so both get it.
    full["UV_HTTP_TIMEOUT"] = "300"
    full["PIP_DEFAULT_TIMEOUT"] = "300"
    full.update(env or {})
    result = subprocess.run(args, cwd=cwd, env=full,
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit(
            f"{' '.join(args)} exited {result.returncode}\n{result.stderr}"
        )


def _time(fn: Callable[[], None]) -> float:
    start = time.perf_counter()
    fn()
    return time.perf_counter() - start


def _requirements(work: Path) -> Path:
    """This book's own lock, exported, minus the local project itself."""
    req = work / "requirements.txt"
    _sh(["uv", "export", "--quiet", "--no-emit-project",
         "--format", "requirements.txt", "-o", str(req)], cwd=CODE)
    return req


def _uv_project(work: Path) -> Path:
    """A copy of this book's project: the lock and what uv needs to read it."""
    proj = work / "uvproj"
    proj.mkdir()
    for name in ("pyproject.toml", "uv.lock", ".python-version", "README.md"):
        shutil.copy(CODE / name, proj / name)
    shutil.copytree(CODE / "src", proj / "src")
    return proj


def _run() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        req = _requirements(work)
        proj = _uv_project(work)
        packages = sum(
            1 for line in req.read_text(encoding="utf8").splitlines()
            if line and line[0].isalpha()
        )
        python = subprocess.run(
            ["uv", "python", "find", (CODE / ".python-version")
             .read_text(encoding="utf8").strip()],
            cwd=work, capture_output=True, text=True, check=True,
        ).stdout.strip()

        uv_cache = work / "uvcache"
        pip_cache = work / "pipcache"
        pipwork = work / "pipwork"
        pipwork.mkdir()
        venv = pipwork / ".venv"

        def uv_once() -> None:
            shutil.rmtree(proj / ".venv", ignore_errors=True)
            _sh(["uv", "sync", "--locked", "--no-install-project", "--quiet"],
                cwd=proj, env={"UV_CACHE_DIR": str(uv_cache)})

        def pip_once() -> None:
            shutil.rmtree(venv, ignore_errors=True)
            _sh([python, "-m", "venv", str(venv)], cwd=pipwork)
            _sh([str(venv / "bin" / "python"), "-m", "pip", "install",
                 "--quiet", "--require-hashes", "-r", str(req)],
                cwd=pipwork, env={"PIP_CACHE_DIR": str(pip_cache)})

        cells: dict[str, list[float]] = {}
        for tool, once, cache in (("uv", uv_once, uv_cache),
                                  ("pip", pip_once, pip_cache)):
            shutil.rmtree(cache, ignore_errors=True)
            cache.mkdir()
            # The cache is emptied before EVERY cold trial, not once before
            # the first: after one run it holds every wheel, so a second
            # "cold" trial taken without emptying it is a warm trial under
            # another name.
            cold: list[float] = []
            for _ in range(TRIALS):
                shutil.rmtree(cache, ignore_errors=True)
                cache.mkdir()
                cold.append(_time(once))
            warm = [_time(once) for _ in range(TRIALS)]
            cells[f"{tool}.cold"] = cold
            cells[f"{tool}.warm"] = warm

        pip_version = subprocess.run(
            [str(venv / "bin" / "python"), "-m", "pip", "--version"],
            capture_output=True, text=True, check=True,
        ).stdout.split()[1]

        return {
            "packages": packages,
            "trials": TRIALS,
            "uv": subprocess.run(["uv", "--version"], capture_output=True,
                                 text=True, check=True).stdout.split()[1],
            "pip": pip_version,
            "python": (CODE / ".python-version")
            .read_text(encoding="utf8").strip(),
            "platform": f"{sys.platform}",
            "cells": cells,
        }


# --------------------------------------------------------------------------
# Formatting the result (the default mode, and the only one CI runs)
# --------------------------------------------------------------------------

def _round(x: float, places: int) -> str:
    return f"{x:.{places}f}"


PLACES = {"uv.cold": 1, "uv.warm": 2, "pip.cold": 1, "pip.warm": 1}


def _values(raw: dict[str, Any]) -> dict[str, str]:
    cells: dict[str, list[float]] = raw["cells"]
    med = {k: statistics.median(v) for k, v in cells.items()}
    v: dict[str, str] = {
        "e2.packages": str(raw["packages"]),
        "e2.trials": str(raw["trials"]),
        # uv's version is NOT emitted here, though the raw data records it:
        # preamble.tex already pins it as \uvver and check_structure --pins
        # holds that macro to every workflow. Two keys for one quantity is
        # two numbers that look like one, and only one of them gets
        # corrected. pip's version is not pinned anywhere -- it is whatever
        # ensurepip bundles with the pinned interpreter -- so it is a
        # measurement and it is emitted.
        "e2.pip.version": str(raw["pip"]),
    }
    for key, places in PLACES.items():
        v[f"e2.{key}"] = _round(med[key], places)

    # EVERY RATIO IS DIVIDED FROM THE PRINTED OPERANDS, not from the exact
    # medians, because a reader with the page in front of them can only
    # divide what is printed. The exact warm ratio here is 99.9 and the
    # printed one is 100.7: report the first and the page says 100 above two
    # numbers that make 101. The guard below is the other half -- if rounding
    # to the page's precision moves a ratio by more than a twentieth, the
    # precision is wrong rather than the ratio, and the build says so.
    def ratio(top: str, bottom: str) -> str:
        shown = float(v[f"e2.{top}"]) / float(v[f"e2.{bottom}"])
        exact = med[top] / med[bottom]
        if abs(shown - exact) > 0.05 * exact:
            raise SystemExit(
                f"e2: {top}/{bottom} is {exact:.3f} exactly and {shown:.3f} "
                f"from the printed figures; print more decimals"
            )
        return _round(shown, 0)

    v["e2.cold.ratio"] = ratio("pip.cold", "uv.cold")
    v["e2.warm.ratio"] = ratio("pip.warm", "uv.warm")
    # The finding the four cells exist to make visible: what a populated
    # cache buys each tool.
    v["e2.uv.cachegain"] = ratio("uv.cold", "uv.warm")
    shown = float(v["e2.pip.cold"]) / float(v["e2.pip.warm"])
    v["e2.pip.cachegain"] = _round(shown, 1)

    # The spread, because a median of three over a real network hides how
    # bad a network can be, and the chapter may not quote a figure it cannot
    # also bound. One uv cold trial on the machine that ran this stalled
    # mid-download for over five minutes; the median is untouched by it and
    # a reader is entitled to know it happened.
    v["e2.uv.cold.worst"] = _round(max(cells["uv.cold"]), 0)
    v["e2.uv.cold.best"] = _round(min(cells["uv.cold"]), 1)
    v["e2.pip.cold.best"] = _round(min(cells["pip.cold"]), 1)
    v["e2.pip.cold.worst"] = _round(max(cells["pip.cold"]), 1)
    return v


def main() -> int:
    ap = argparse.ArgumentParser(description="Experiment E2")
    ap.add_argument("--run", action="store_true",
                    help="perform the benchmark and rewrite the raw data")
    args = ap.parse_args()

    if args.run:
        DATA.parent.mkdir(parents=True, exist_ok=True)
        raw = _run()
        DATA.write_text(json.dumps(raw, indent=2) + "\n", encoding="utf8")
        print(f"  wrote {DATA.relative_to(ROOT)}")

    if not DATA.is_file():
        raise SystemExit(
            f"{DATA.relative_to(ROOT)} is missing: run this script with "
            f"--run once, on a machine with a network, and commit the result"
        )
    raw = json.loads(DATA.read_text(encoding="utf8"))
    values = _values(raw)
    lines = ["% Generated by code/measure/e2_install.py --- do not edit."]
    for key, value in values.items():
        lines.append(f"\\pyvaltext{{{key}}}{{{value}}}"
                     if key.endswith("version")
                     else f"\\pyval{{{key}}}{{{value}}}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf8")
    for key, value in values.items():
        print(f"  {key:20} {value}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
