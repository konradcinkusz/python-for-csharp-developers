#!/usr/bin/env python3
"""Ask both pinned checkers what they make of ch03/where_it_lies.py.

The chapter's central claim is that a type hint is a claim nobody checks
unless you invite a checker, and that the tools you can invite do not
accept the same invitation. That is a claim about three tools, so it is
measured here rather than asserted on the page: this script runs pyright
and mypy over ch03/where_it_lies.py, runs all three over ch03/defaults.py,
and writes what each said.

ruff is run with --ignore-noqa on the second file, because the listing
carries a noqa comment so that `make code` stays green. Without the flag
this script would measure the comment rather than the code.

Three things it holds itself to:

  * The diagnostics come from each tool's own machine-readable output --
    pyright's --outputjson and mypy's error lines -- rather than from a
    console paste. A transcript nobody ran reads exactly like one that was.
  * Nothing machine-dependent reaches the page. pyright reports its own
    running time and absolute paths; neither is written out. The versions
    are read from the installed distributions, so the transcript records
    which pair of checkers produced the verdict and `make verify` fails
    when a pin moves and the page does not.
  * The invariant the prose rests on is asserted, not assumed: every
    top-level function in the file under test declares that it returns an
    int. If a later edit breaks that, this script stops rather than
    quietly measuring a different claim.

Run from code/:   uv run python measure/checkers.py
"""

from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
import tempfile
from importlib.metadata import version
from pathlib import Path
from typing import NamedTuple, cast

CODE = Path(__file__).resolve().parents[1]
ROOT = CODE.parent
VALUES = ROOT / "figures" / "values" / "ch03.tex"
TRANSCRIPTS = ROOT / "figures" / "transcripts"

LIES = "ch03/where_it_lies.py"
DEFAULTS = "ch03/defaults.py"
WIDTH = 79

MYPY_LINE = re.compile(
    r"^(?P<file>[^:]+):(?P<line>\d+): (?P<severity>\w+): "
    r"(?P<message>.*?)\s+\[(?P<code>[\w-]+)\]$"
)


class Finding(NamedTuple):
    line: int
    code: str
    message: str


def declared_int_returns(path: Path) -> int:
    """How many top-level functions declare `-> int`, from the syntax tree.

    The chapter says "every function below declares that it returns an
    int". That is a property of the file, so it is read out of the file.
    """
    tree = ast.parse(path.read_text(encoding="utf8"))
    total, declared = 0, 0
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        if node.name == "main":
            continue
        total += 1
        returns = node.returns
        if isinstance(returns, ast.Name) and returns.id == "int":
            declared += 1
    if total != declared:
        raise SystemExit(
            f"{path.name}: {total} functions, {declared} declaring -> int; "
            f"the chapter's sentence is no longer true of the file"
        )
    return declared


def mapping(value: object) -> dict[str, object]:
    """Narrow a decoded JSON value to a string-keyed mapping.

    `isinstance(value, dict)` narrows to dict[Unknown, Unknown] under a
    strict checker, which is the complaint section 5 of the chapter is
    about, and it fired on this script while the script was being written
    to measure it. The cast is the one place this file takes
    responsibility for a shape the checker cannot see.
    """
    if not isinstance(value, dict):
        return {}
    return cast("dict[str, object]", value)


def sequence(value: object) -> list[object]:
    """The same narrowing, for a JSON array."""
    if not isinstance(value, list):
        return []
    return cast("list[object]", value)


def run_pyright(target: str) -> list[Finding]:
    """pyright, in whatever mode code/pyproject.toml configures."""
    result = subprocess.run(
        [sys.executable, "-m", "pyright", "--outputjson", target],
        cwd=CODE,
        capture_output=True,
        text=True,
    )
    if not result.stdout.strip():
        raise SystemExit(f"pyright produced no JSON: {result.stderr[:400]}")
    report = mapping(json.loads(result.stdout))
    findings: list[Finding] = []
    for item in sequence(report.get("generalDiagnostics", [])):
        entry = mapping(item)
        if entry.get("severity") != "error":
            continue
        start = mapping(mapping(entry.get("range", {})).get("start", {}))
        findings.append(
            Finding(
                line=int(str(start.get("line", -1))) + 1,
                code=str(entry.get("rule", "")),
                message=str(entry.get("message", "")).splitlines()[0],
            )
        )
    return findings


def run_mypy(target: str) -> list[Finding]:
    """mypy --strict, with a throwaway cache so the answer cannot depend
    on what a previous run happened to leave behind."""
    with tempfile.TemporaryDirectory() as cache:
        result = subprocess.run(
            [
                sys.executable, "-m", "mypy", "--strict",
                "--no-color-output", "--no-error-summary",
                "--cache-dir", cache, target,
            ],
            cwd=CODE,
            capture_output=True,
            text=True,
        )
    findings: list[Finding] = []
    for raw in result.stdout.splitlines():
        match = MYPY_LINE.match(raw.strip())
        if match is None or match["severity"] != "error":
            continue
        findings.append(
            Finding(
                line=int(match["line"]),
                code=match["code"],
                message=match["message"],
            )
        )
    return findings


def run_ruff(target: str) -> list[Finding]:
    """ruff, with the file's own noqa comments ignored.

    The listing under test carries a noqa so that `make code` passes;
    honouring it here would measure the comment rather than the code.
    """
    result = subprocess.run(
        [
            sys.executable, "-m", "ruff", "check",
            "--ignore-noqa", "--output-format", "json", target,
        ],
        cwd=CODE,
        capture_output=True,
        text=True,
    )
    findings: list[Finding] = []
    for item in sequence(json.loads(result.stdout or "[]")):
        entry = mapping(item)
        location = mapping(entry.get("location", {}))
        findings.append(
            Finding(
                line=int(str(location.get("row", 0))),
                code=str(entry.get("code", "")),
                message=str(entry.get("message", "")),
            )
        )
    return findings


def render(name: str, tool_version: str, findings: list[Finding]) -> list[str]:
    """One tool's verdict, wrapped to the page rather than to a terminal."""
    head = f"{name} {tool_version}: {len(findings)} error(s)"
    lines = [head]
    for found in findings:
        lines.append(f"  line {found.line}  {found.code}")
        body = f"    {found.message}"
        while len(body) > WIDTH:
            cut = body.rfind(" ", 0, WIDTH)
            cut = WIDTH if cut <= 4 else cut
            lines.append(body[:cut])
            body = "      " + body[cut:].lstrip()
        lines.append(body)
    return lines


def guard(lines: list[str]) -> None:
    for number, line in enumerate(lines, start=1):
        if any(ord(ch) > 127 or ord(ch) < 32 for ch in line):
            raise SystemExit(f"checkers: line {number} is not plain ASCII")
        if len(line) > WIDTH:
            raise SystemExit(
                f"checkers: line {number} is {len(line)} columns, over {WIDTH}"
            )


def write(path: Path, lines: list[str]) -> None:
    """Guard first, then write: a transcript the page cannot set is worse
    than no transcript, and the guard is what makes that impossible."""
    guard(lines)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf8")
    print(f"  {path.name}: {len(lines)} line(s)")


def main() -> int:
    functions = declared_int_returns(CODE / LIES)
    lies_pyright = run_pyright(LIES)
    lies_mypy = run_mypy(LIES)

    lines = [
        f"{LIES}: {functions} functions, every one declaring -> int,",
        "every one returning a str.",
        "",
    ]
    lines += render("pyright", version("pyright"), lies_pyright)
    lines.append("")
    lines += render("mypy --strict", version("mypy"), lies_mypy)
    write(TRANSCRIPTS / "ch03-checkers.txt", lines)

    def_pyright = run_pyright(DEFAULTS)
    def_mypy = run_mypy(DEFAULTS)
    def_ruff = run_ruff(DEFAULTS)

    lines = [
        f"{DEFAULTS}: one mutable default argument, correctly annotated.",
        "",
    ]
    lines += render("pyright", version("pyright"), def_pyright)
    lines.append("")
    lines += render("mypy --strict", version("mypy"), def_mypy)
    lines.append("")
    lines += render("ruff --ignore-noqa", version("ruff"), def_ruff)
    write(TRANSCRIPTS / "ch03-three-tools.txt", lines)

    values = {
        "ch03.lies.functions": functions,
        "ch03.pyright.errors": len(lies_pyright),
        "ch03.mypy.errors": len(lies_mypy),
        "ch03.defaults.pyright": len(def_pyright),
        "ch03.defaults.mypy": len(def_mypy),
        "ch03.defaults.ruff": len(def_ruff),
    }
    out = ["% Generated by code/measure/checkers.py --- do not edit."]
    out += [f"\\pyval{{{key}}}{{{value}}}" for key, value in values.items()]
    VALUES.parent.mkdir(parents=True, exist_ok=True)
    VALUES.write_text("\n".join(out) + "\n", encoding="utf8")
    for key, value in values.items():
        print(f"  {key:26} {value}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
