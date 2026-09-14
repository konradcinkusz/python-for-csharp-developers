#!/usr/bin/env python3
"""Compare what the two editions' cross-references actually resolved to.

tools/parity.py compares the *source*: the same \\label names, the same \\ref
names. That is necessary and not sufficient. This compares the *result*, read
out of the .aux files after a full build, and catches the failure the source
cannot show:

    \\label{ch:asyncio} resolves to chapter 8 in English and 9 in Polish

which happens the moment a \\part, a chapter, a section or a listing exists
in one edition and not the other. Every "see Chapter 8" and every listing
number then points somewhere different in the two books, and neither build
emits a warning, because both are internally consistent.

Page numbers legitimately differ -- Polish prose runs longer -- so only the
reference *number* is compared.

Usage:  python3 tools/reflist.py [main-en.aux main-pl.aux]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NEWLABEL = re.compile(r"\\newlabel\{([^}]*)\}\{\{([^}]*)\}\{([^}]*)\}")


def collect(aux: Path, seen: set[Path] | None = None) -> dict[str, str]:
    """Read an .aux and everything it \\@input{}s. Returns {label: number}."""
    seen = seen if seen is not None else set()
    aux = aux.resolve()
    if aux in seen or not aux.is_file():
        return {}
    seen.add(aux)
    text = aux.read_text(encoding="utf8", errors="replace")
    out = {m.group(1): m.group(2) for m in NEWLABEL.finditer(text)}
    for m in re.finditer(r"\\@input\{([^}]*)\}", text):
        out.update(collect(ROOT / m.group(1), seen))
    return out


def main() -> int:
    args = sys.argv[1:]
    en_aux = Path(args[0]) if args else ROOT / "main-en.aux"
    pl_aux = Path(args[1]) if len(args) > 1 else ROOT / "main-pl.aux"

    for p in (en_aux, pl_aux):
        if not p.is_file():
            print(f"  FAIL  {p} missing -- build both editions first")
            return 1

    en, pl = collect(en_aux), collect(pl_aux)
    fails = 0

    for k in sorted(set(en) - set(pl)):
        print(f"  FAIL  label {k!r} resolves in en but not in pl")
        fails += 1
    for k in sorted(set(pl) - set(en)):
        print(f"  FAIL  label {k!r} resolves in pl but not in en")
        fails += 1
    for k in sorted(set(en) & set(pl)):
        if en[k] != pl[k]:
            print(f"  FAIL  label {k!r} numbers differently: "
                  f"en={en[k]!r} pl={pl[k]!r}")
            fails += 1

    print("-" * 68)
    print(f"  {len(en)} labels in en, {len(pl)} in pl, {fails} mismatches")

    # A check that passes because it read nothing is worse than no check. The
    # aux tree is a \@input{} chain, so being handed only the main file finds
    # zero labels in both editions and reports zero mismatches -- which looks
    # exactly like success.
    if not en or not pl:
        print("  FAIL  no labels found. The per-program .aux files are part of")
        print("        the \\@input{} chain and must be present, not just the")
        print("        main file.")
        return 1

    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
