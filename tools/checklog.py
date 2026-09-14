#!/usr/bin/env python3
"""Decide whether a LaTeX run actually succeeded.

`grep '^!' main.log` is the habit inherited from the companion volumes and it
is not sufficient here, for two reasons that cost this repository a real bug:

  * with -file-line-error, an error line begins with a PATH, not with `!`
    (`./preamble.tex:735: Illegal parameter number ...`), so the usual grep
    cannot see it;
  * -interaction=nonstopmode recovers from errors and still writes a PDF, so
    the exit code and the existence of the PDF both say "fine".

Between them, a broken \\IfFileExists branch in a sibling repository stopped
siunitx from loading at all -- and the decimal comma silently did not work in
a build everyone believed was green. This file is that repository's checker,
copied whole; the reasoning is theirs and it holds here unchanged.

Usage:
    tools/checklog.py main-en.log [main-pl.log ...]
    tools/checklog.py --summary main-en.log        # machine-readable one-liner

Exit code is non-zero if any log carries an error, an unresolved reference, or
an overfull vbox -- the three things that must never reach a reader.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

RE_BANG = re.compile(r"^! (.*)$", re.M)
RE_FILELINE = re.compile(r"^(?:\./|/)[^\s:]+:\d+: (.*)$", re.M)
RE_UNDEF_REF = re.compile(r"Reference `([^']+)' on page \d+ undefined", re.M)
RE_UNDEF_CIT = re.compile(r"Citation `([^']+)' on page \d+ undefined", re.M)
RE_HBOX = re.compile(r"Overfull \\hbox \(([\d.]+)pt")
RE_VBOX = re.compile(r"Overfull \\vbox \(([\d.]+)pt")
# WHERE a vbox happened, and it matters that TeX says this two different ways:
#
#   Overfull \vbox (12.3pt too high) has occurred while \output is active [456]
#   Overfull \vbox (5.0pt too high) detected at line 1234
#
# The first is a PAGE that came out too tall, and its position moves when
# anything before it moves. The second is a FIXED BOX -- a \parbox, a minipage,
# a tcolorbox -- that is too tall for the space it was given, and it is
# invariant under repagination. Reporting only the size makes the two
# indistinguishable, and this repository lost a cycle to exactly that: a glue
# change moved the whole book and the two reported sizes came back identical,
# which was the tell that at least one of them was not a page at all.
#
# The source file is tracked too, because "detected at line 1234" without a
# file is not a location. TeX brackets each file it opens, so the innermost
# unclosed `(` at the point of the complaint is the file being read.
RE_SHIPOUT = re.compile(r"\[(\d+)[^\]]*\]")
RE_VBOX_WHERE = re.compile(
    r"has occurred while \\output is active|detected at line (\d+)")
# Document content only. A .sty or .cls is read in the preamble and can
# never be where a typeset box was built, so matching them would report the
# last package loaded and nothing useful.
RE_FILE_OPEN = re.compile(r"\((\.{0,2}/[^\s()]*\.(?:tex|ind|toc))")
# TeX names an overfull hbox by the SOURCE lines of the paragraph it broke,
# and then prints the offending line itself. Both are wanted: the line range
# says which paragraph and the text says which run inside it could not break.
RE_HBOX_WHERE = re.compile(r"in paragraph at lines (\d+)--(\d+)"
                           r"|detected at line (\d+)")
RE_PAGES = re.compile(r"Output written on \S+ \((\d+) pages")
RE_MISSING_VAL = re.compile(r"No computed values found")
# Warnings that are always worth surfacing. Font substitution noise is not.
RE_WARN = re.compile(r"^(?:LaTeX|Package|Class) (\w+ )?Warning: (.*)$", re.M)
WARN_IGNORE = ("Font shape", "Some font shapes", "Size substitutions",
               "Token not allowed", "There were undefined references")

# Warnings that must FAIL a build rather than be printed and shrugged at.
#
# "Label(s) may have changed" was in WARN_IGNORE, and report() never failed on
# a warning anyway, so a build that stopped rerunning while the .aux was still
# moving exited 0 with a stale number on the page. Two things in this book are
# carried through the .aux by \@newl@bel: every \ref and every page number in
# the contents. A non-converged run fails SILENTLY -- the failure is a wrong
# number, not a missing one, which is the same shape as a console block nobody
# ran.
#
# Reproduced rather than reasoned: a minimal document recording a value through
# \@newl@bel, run to convergence at 45 and then changed to record 46, printed
# the STALE 45, emitted "LaTeX Warning: Label(s) may have changed" and exited 0.
#
HARD_WARN = ("Label(s) may have changed", "Rerun to get", "Marginpar on page")

HBOX_BUDGET = 15.0   # pt. Anything above this visibly runs into the margin.


def _vbox_where(text: str, pos: int) -> str:
    """Describe where an overfull vbox at `pos` happened, as TeX reported it.

    Returns "PDF page N" for a page that came out too tall, or
    "<file> line N" for a fixed box that did not fit the space it was given.
    The two need different fixes and only TeX knows which is which.
    """
    tail = text[pos:pos + 300].replace("\n", "")
    m = RE_VBOX_WHERE.search(tail)
    if m and m.group(1):
        return f"line {m.group(1)}, {_open_file(text, pos)}"
    page = RE_SHIPOUT.search(tail)
    return f"on PDF page {page.group(1)}" if page else "at an unknown location"


def _hbox_where(text: str, pos: int) -> tuple:
    """Where an overfull hbox at `pos` happened, and the line TeX could not set.

    This exists because CI and the container that publishes the PDF have
    different font metrics, so an over-budget hbox is nearly always reported
    by the machine that cannot see it. Reporting the size alone -- which is
    what this tool used to do -- costs a whole CI cycle guessing which line it
    is. The vbox reporting below was given a location for exactly that reason;
    the hbox reporting was not, and P24 paid for the omission.
    """
    head = text[pos:pos + 200]
    m = RE_HBOX_WHERE.search(head)
    if m and m.group(1):
        where = f"source lines {m.group(1)}--{m.group(2)}, {_open_file(text, pos)}"
    elif m and m.group(3):
        where = f"source line {m.group(3)}, {_open_file(text, pos)}"
    else:
        where = _open_file(text, pos)
    # The line TeX could not set follows the complaint. Its first font switch
    # is noise; what is wanted is the words, so they are stripped out.
    body = text[pos:pos + 700].split("\n")
    line = " ".join(body[1:3]).strip() if len(body) > 1 else ""
    line = re.sub(r"\\[A-Za-z@/0-9.]+(?:/[^ ]*)?", " ", line)
    line = re.sub(r"\s+", " ", line).strip()
    return where, line[:96]


def _open_file(text: str, pos: int) -> str:
    """The last file TeX opened before `pos`.

    Deliberately NOT a bracket-matching stack. A TeX log is full of unmatched
    parentheses in ordinary prose and in package chatter, so a stack empties
    itself within a few thousand characters and then reports nothing -- which
    was tried, and did. The last file opened is a starting point rather than a
    guarantee, and the report says so rather than claiming more than it knows.
    """
    opens = list(RE_FILE_OPEN.finditer(text, 0, pos))
    return (f"in or after {opens[-1].group(1)}" if opens
            else "in a file TeX did not name")


def analyse(path: Path) -> dict:
    text = path.read_text(encoding="utf8", errors="replace")
    errors = RE_BANG.findall(text) + RE_FILELINE.findall(text)
    warns = [
        f"{m.group(1) or ''}{m.group(2)}".strip()
        for m in RE_WARN.finditer(text)
        if not any(s in m.group(2) for s in WARN_IGNORE)
    ]
    h = sorted((float(x) for x in RE_HBOX.findall(text)), reverse=True)
    v = sorted((float(x) for x in RE_VBOX.findall(text)), reverse=True)
    v_pages = [(float(m.group(1)), _vbox_where(text, m.end()))
               for m in RE_VBOX.finditer(text)]
    v_pages.sort(key=lambda t: -t[0])
    h_where = [(float(m.group(1)), *_hbox_where(text, m.end()))
               for m in RE_HBOX.finditer(text)
               if float(m.group(1)) > HBOX_BUDGET]
    h_where.sort(key=lambda t: -t[0])
    pages = RE_PAGES.search(text)
    return {
        "file": path.name,
        "errors": errors,
        "warnings": warns,
        "hard_warnings": [w for w in warns if any(s in w for s in HARD_WARN)],
        "undef_refs": RE_UNDEF_REF.findall(text),
        "undef_cits": RE_UNDEF_CIT.findall(text),
        "hbox": h,
        "vbox": v,
        "vbox_pages": v_pages,
        "over_budget": [x for x in h if x > HBOX_BUDGET],
        "over_budget_where": h_where,
        "pages": int(pages.group(1)) if pages else None,
        "no_values": bool(RE_MISSING_VAL.search(text)),
    }


def report(r: dict) -> bool:
    ok = True
    print(f"== {r['file']} ==")
    print(f"  pages           : {r['pages']}")
    if r["errors"]:
        ok = False
        print(f"  ERRORS          : {len(r['errors'])}")
        for e in r["errors"][:12]:
            print(f"      {e}")
    else:
        print("  errors          : 0")
    if r["undef_refs"] or r["undef_cits"]:
        ok = False
        print(f"  UNRESOLVED REFS : {sorted(set(r['undef_refs'] + r['undef_cits']))}")
    else:
        print("  unresolved refs : 0")
    print(f"  overfull hbox   : {len(r['hbox'])} "
          f"{[round(x, 1) for x in r['hbox'][:8]]}")
    if r["over_budget"]:
        ok = False
        print(f"  OVER {HBOX_BUDGET:.0f} pt BUDGET : {[round(x, 1) for x in r['over_budget']]}")
        for size, where, line in r["over_budget_where"][:5]:
            print(f"      {size:6.1f} pt too wide, {where}")
            if line:
                print(f"          [{line}]")
        print("      An over-budget hbox is an unbreakable run: a long \\code{},")
        print("      a chain of maths spans, a word-formula. Put it in a display")
        print("      or start a sentence with it; rewording moves it elsewhere.")
    if r["vbox"]:
        ok = False
        print(f"  OVERFULL VBOX   : {len(r['vbox'])} {[round(x, 1) for x in r['vbox'][:5]]}")
        for size, where in r["vbox_pages"][:5]:
            print(f"      {size:6.1f} pt too high, {where}")
        print("      A vbox means a block grew past the space it had and could")
        print("      not break. Split the table; do not shrink the text.")
        print("      READ THE LOCATION: `PDF page N` is a page that came out")
        print("      too tall and moves when anything before it moves; a file")
        print("      and line is a FIXED box -- a parbox, a minipage, a")
        print("      tcolorbox -- that does not. They need different fixes.")
        print("      It is printed because the two TeX installations this book")
        print("      builds on paginate differently, so the machine that must")
        print("      fix it is usually not the one that saw it.")
    else:
        print("  overfull vbox   : 0")
    if r["no_values"]:
        ok = False
        print("  NO COMPUTED VALUES: every \\val{} printed a marker. Run `make numbers`.")
    if r["hard_warnings"]:
        ok = False
        print(f"  NON-CONVERGENCE : {len(r['hard_warnings'])}")
        for w in r["hard_warnings"][:6]:
            print(f"      {w}")
        print("      The build stopped rerunning while the .aux was still")
        print("      moving, so a cross-reference or a page number may be")
        print("      printing a stale value. Run latexmk again.")
    if r["warnings"]:
        print(f"  warnings        : {len(r['warnings'])}")
        for w in r["warnings"][:6]:
            print(f"      {w}")
    return ok


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("logs", nargs="+", type=Path)
    p.add_argument("--summary", action="store_true")
    a = p.parse_args()
    ok = True
    for path in a.logs:
        if not path.exists():
            print(f"== {path} == MISSING")
            ok = False
            continue
        r = analyse(path)
        if a.summary:
            print(f"{r['file']}: pages={r['pages']} errors={len(r['errors'])} "
                  f"refs={len(set(r['undef_refs']))} hbox={len(r['hbox'])} "
                  f"vbox={len(r['vbox'])} warn={len(r['warnings'])}")
            ok &= not (r["errors"] or r["undef_refs"] or r["vbox"]
                       or r["over_budget"] or r["hard_warnings"])
        else:
            ok &= report(r)
    return 0 if ok else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        # `checklog.py ... | head` closes the pipe. Exiting quietly is the
        # right behaviour; a traceback here reads as a failure of the check.
        sys.exit(0)
