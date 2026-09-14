#!/usr/bin/env python3
"""Prove that the Polish and English editions are the same book.

The two editions live in parallel trees (chapters/en, chapters/pl, ...).
Prose is duplicated on purpose; *structure* must not be. This script extracts
an ordered structural signature from each source file and compares the twins.

It is deliberately stricter than "the same number of sections". A book whose
every listing is a file and whose every exercise is a starter and a test
breaks the moment the Polish edition prints a different file, a different
exercise key or a different number from the English one, because the reader
of either edition opens the same repository.

Run:  python3 tools/parity.py            (from the repository root)
Exit: 0 clean, 1 divergence, 2 usage error.

A deliberate divergence is declared by putting

    % parity: allow-divergence <reason>

in BOTH files at the corresponding point. The next token is then dropped from
both signatures. Those markers are debt and `make debt` counts them.

Lineage: this is the math book's tools/parity.py with the frame machinery
removed and the listing, exercise and transcript macros added. The check
numbers are kept, so a note in a sibling repository about C12 or C15 is about
the same thing here.
"""

from __future__ import annotations

import difflib
import hashlib
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANGS = ("en", "pl")
TREES = ("chapters", "appendices", "frontmatter")

# Admonitions and the structural environments. A trap box present in one
# edition and not the other means the two editions correct different
# misconceptions, which is a content difference wearing a translation's
# clothes.
BOXES = (
    "note warning csbox versionbox trapbox verifybox exercisebox projectbox exercise "
    "enumerate itemize description tabularx figure"
).split()

# In-source listings. Their BODY is compared byte for byte: listing comments
# stay English in both editions by standing rule, so a body that differs is a
# body that was edited in one edition only.
LISTING_ENVS = ("python", "csharp", "shellcmd", "tomlcode", "yamlcode",
                "jsoncode", "console", "lstlisting", "verbatim")

MATH_ENVS = ("equation", "equation*", "align", "align*", "gather", "gather*",
             "multline", "multline*")

# Macros that carry a payload which must be identical across editions,
# because the payload is a path, a key or a cross-reference rather than
# prose. The number is how many brace groups the macro takes and the tuple
# says which of them are compared (0-based); the rest is caption, translated.
KEYED: dict[str, tuple[str, int, tuple[int, ...]]] = {
    "label": ("LABEL", 1, (0,)),
    "ref": ("REF", 1, (0,)),
    "pageref": ("REF", 1, (0,)),
    "val": ("VAL", 1, (0,)),
    "valtext": ("VAL", 1, (0,)),
    "mermaidfig": ("FIG", 3, (0,)),
    "pyfile": ("LISTFILE", 3, (0, 2)),
    "csfile": ("LISTFILE", 3, (0, 2)),
    "pyregion": ("LISTREGION", 4, (0, 1, 3)),
    "transcript": ("TRANSCRIPT", 1, (0,)),
    "chapterstub": ("STUB", 1, ()),
    "index": ("INDEX", 1, ()),
}

# Macros with no payload worth comparing, but whose presence and position are
# structural.
BARE = {
    "chapter": "CHAPTER", "section": "SECTION", "subsection": "SUBSECTION",
    "listofdiagrams": "LISTOFDIAGRAMS", "listofexercises": "LISTOFEXERCISES",
    "item": "ITEM", "toprule": "TOPRULE", "midrule": "MIDRULE",
    "bottomrule": "BOTTOMRULE",
}

ALLOW_RE = re.compile(r"^[ \t]*%[ \t]*parity:[ \t]*allow-divergence\b(.*)$", re.M)
COMMENT_RE = re.compile(r"(?<!\\)%.*$", re.M)


@dataclass
class Token:
    kind: str
    payload: str
    line: int

    def key(self) -> str:
        return f"{self.kind}({self.payload})" if self.payload else self.kind


@dataclass
class Doc:
    path: Path
    tokens: list[Token] = field(default_factory=list)
    labels: list[str] = field(default_factory=list)
    refs: list[str] = field(default_factory=list)
    vals: list[str] = field(default_factory=list)
    figs: list[str] = field(default_factory=list)
    exercises: list[str] = field(default_factory=list)
    allows: int = 0


def _balanced(src: str, i: int) -> tuple[str, int]:
    """Read a brace group starting at src[i] == '{'. Returns (body, next)."""
    while i < len(src) and src[i] in " \t\n":
        i += 1
    if i >= len(src) or src[i] != "{":
        return "", i
    depth, j = 0, i
    while j < len(src):
        c = src[j]
        if c == "\\":
            j += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return src[i + 1:j], j + 1
        j += 1
    return src[i + 1:], len(src)


def _optional(src: str, i: int) -> int:
    """Skip a [..] optional argument at src[i], if there is one."""
    if i < len(src) and src[i] == "[":
        j = src.find("]", i)
        return len(src) if j < 0 else j + 1
    return i


PROSE_IN_MATH = re.compile(
    r"\\(?:text|textrm|textit|textbf|mbox|hbox|intertext)\s*\{[^{}]*\}")


def _norm_math(body: str) -> str:
    """Only the mathematical content of a maths body survives.

    Whitespace and \\, spacing are noise, and so is the wording inside a
    \\text{}, which is prose and is translated. Nothing else is stripped: a
    sign or an exponent that differs between the editions must show up.
    """
    b = COMMENT_RE.sub("", body)
    b = PROSE_IN_MATH.sub("<prose>", b)
    b = re.sub(r"\\[,;:!> ]", "", b)
    b = re.sub(r"\s+", "", b)
    return hashlib.sha1(b.encode("utf8")).hexdigest()[:10]


def _digest(body: str) -> str:
    return hashlib.sha1(body.encode("utf8")).hexdigest()[:10]


def tokenise(path: Path) -> Doc:
    src = path.read_text(encoding="utf8")
    doc = Doc(path=path)
    allow_lines = {src[:m.start()].count("\n") + 1 for m in ALLOW_RE.finditer(src)}
    doc.allows = len(allow_lines)

    src_nc = COMMENT_RE.sub("", src)
    i, n = 0, len(src_nc)

    def line_at(pos: int) -> int:
        return src_nc.count("\n", 0, pos) + 1

    def emit(kind: str, payload: str, pos: int) -> None:
        doc.tokens.append(Token(kind, payload, line_at(pos)))

    while i < n:
        c = src_nc[i]

        if c == "$":
            display = src_nc.startswith("$$", i)
            close = "$$" if display else "$"
            j = i + len(close)
            while j < n:
                if src_nc[j] == "\\":
                    j += 2
                    continue
                if src_nc.startswith(close, j):
                    break
                j += 1
            body = src_nc[i + len(close):j]
            doc.vals.extend(re.findall(r"\\val(?:text)?\{([^{}]*)\}", body))
            emit("MATH", _norm_math(body), i)
            i = j + len(close)
            continue

        if src_nc.startswith("\\[", i):
            j = src_nc.find("\\]", i)
            j = n if j < 0 else j
            body = src_nc[i + 2:j]
            doc.vals.extend(re.findall(r"\\val(?:text)?\{([^{}]*)\}", body))
            emit("MATH", _norm_math(body), i)
            i = j + 2
            continue

        if c != "\\":
            i += 1
            continue

        m = re.match(r"\\([A-Za-z@]+)\*?", src_nc[i:])
        if not m:
            i += 2
            continue
        name = m.group(1)
        after = i + m.end()

        if name in ("begin", "end"):
            body, nxt = _balanced(src_nc, after)
            if name == "begin":
                if body in MATH_ENVS:
                    endtok = "\\end{%s}" % body
                    j = src_nc.find(endtok, nxt)
                    j = n if j < 0 else j
                    inner = src_nc[nxt:j]
                    doc.vals.extend(re.findall(r"\\val(?:text)?\{([^{}]*)\}", inner))
                    emit("MATH", _norm_math(inner), i)
                    i = j + len(endtok)
                    continue
                if body in LISTING_ENVS:
                    endtok = "\\end{%s}" % body
                    j = src_nc.find(endtok, nxt)
                    j = n if j < 0 else j
                    inner = src_nc[nxt:j]
                    inner = inner[_optional(inner, 0):] if inner.startswith("[") else inner
                    emit("LISTING", f"{body}:{_digest(inner.strip())}", i)
                    i = j + len(endtok)
                    continue
                if body == "exercise":
                    # \begin{exercise}{key}{title}: the key is a file stem and
                    # must be identical in both editions; the title is prose.
                    key, pos = _balanced(src_nc, nxt)
                    _title, pos = _balanced(src_nc, pos)
                    doc.exercises.append(key.strip())
                    emit("EXERCISE", key.strip(), i)
                    emit("BEGIN", body, i)
                    i = pos
                    continue
                if body in BOXES:
                    emit("BEGIN", body, i)
            else:
                if body in BOXES:
                    emit("END", body, i)
            i = nxt
            continue

        if name in KEYED:
            kind, nargs, compare = KEYED[name]
            pos = _optional(src_nc, after)
            args = []
            for _ in range(nargs):
                body, pos = _balanced(src_nc, pos)
                args.append(body.strip())
            payload = "|".join(args[k] for k in compare if k < len(args))
            if kind == "LABEL":
                doc.labels.append(args[0])
            elif kind == "REF":
                doc.refs.append(args[0])
            elif kind == "VAL":
                doc.vals.append(args[0])
            elif kind == "FIG":
                doc.figs.append(args[0])
            elif kind == "EXERCISE":
                doc.exercises.append(args[0])
            emit(kind, payload, i)
            i = pos
            continue

        if name in BARE:
            emit(BARE[name], "", i)
            i = after
            continue

        i = after

    if allow_lines:
        keep, dropped = [], set()
        for t in doc.tokens:
            cand = min((l for l in allow_lines if l <= t.line and l not in dropped),
                       default=None)
            if cand is not None and t.line - cand <= 3:
                dropped.add(cand)
                continue
            keep.append(t)
        doc.tokens = keep
    return doc


# --------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------

class Report:
    def __init__(self) -> None:
        self.fail: list[str] = []
        self.warn: list[str] = []
        self.ok: list[str] = []

    def bad(self, check: str, msg: str) -> None:
        self.fail.append(f"[{check}] {msg}")

    def soft(self, check: str, msg: str) -> None:
        self.warn.append(f"[{check}] {msg}")

    def good(self, check: str, msg: str) -> None:
        self.ok.append(f"[{check}] {msg}")


def check_filesets(rep: Report) -> list[tuple[Path, Path]]:
    pairs = []
    for tree in TREES:
        base = ROOT / tree
        if not base.is_dir():
            continue
        sets = {}
        for lang in LANGS:
            d = base / lang
            sets[lang] = {p.name for p in d.glob("*.tex")} if d.is_dir() else set()
        for f in sorted(sets["en"] - sets["pl"]):
            rep.bad("C1-files", f"{tree}/en/{f} has no Polish twin")
        for f in sorted(sets["pl"] - sets["en"]):
            rep.bad("C1-files", f"{tree}/pl/{f} has no English twin")
        for f in sorted(sets["en"] & sets["pl"]):
            pairs.append((base / "en" / f, base / "pl" / f))
    if not pairs:
        rep.soft("C1-files", "no paired .tex sources found yet")
    else:
        rep.good("C1-files", f"{len(pairs)} file pairs")
    return pairs


def check_lang_catalogue(rep: Report) -> None:
    defs = {}
    for lang in LANGS:
        p = ROOT / "lang" / f"{lang}.tex"
        if not p.is_file():
            rep.bad("C3-lang", f"lang/{lang}.tex missing")
            return
        src = COMMENT_RE.sub("", p.read_text(encoding="utf8"))
        names = set(re.findall(
            r"\\(?:newcommand|providecommand|DeclareRobustCommand)\*?\{?\\([A-Za-z@]+)\}?",
            src))
        defs[lang] = names
    for miss in sorted(defs["en"] - defs["pl"]):
        rep.bad("C3-lang", f"\\{miss} defined in en but not pl")
    for miss in sorted(defs["pl"] - defs["en"]):
        rep.bad("C3-lang", f"\\{miss} defined in pl but not en")
    if defs["en"] == defs["pl"]:
        rep.good("C3-lang", f"{len(defs['en'])} macros defined in both")


def check_signature(rep: Report, en: Doc, pl: Doc) -> None:
    name = en.path.name
    a = [t.key() for t in en.tokens]
    b = [t.key() for t in pl.tokens]
    if a == b:
        rep.good("C4-structure", f"{name}: {len(a)} tokens")
        return
    for k in range(max(len(a), len(b))):
        x = a[k] if k < len(a) else None
        y = b[k] if k < len(b) else None
        if x != y:
            el = en.tokens[k].line if k < len(en.tokens) else "EOF"
            pll = pl.tokens[k].line if k < len(pl.tokens) else "EOF"
            rep.bad("C4-structure",
                    f"{name}: diverge at token {k+1} -- "
                    f"en:{el} {x or '<end of file>'} != pl:{pll} {y or '<end of file>'}")
            break


def check_sets(rep: Report, en: Doc, pl: Doc) -> None:
    name = en.path.name
    for what, ea, pa, check in (
        ("label", en.labels, pl.labels, "C5-labels"),
        ("value key", en.vals, pl.vals, "C7-values"),
        ("diagram key", en.figs, pl.figs, "C9-diagrams"),
        ("exercise key", en.exercises, pl.exercises, "C11-exercises"),
    ):
        se, sp = set(ea), set(pa)
        for k in sorted(se - sp):
            rep.bad(check, f"{name}: {what} {k!r} in en only")
        for k in sorted(sp - se):
            rep.bad(check, f"{name}: {what} {k!r} in pl only")


def check_value_defs(rep: Report, docs: list[Doc]) -> None:
    defined = set()
    vdir = ROOT / "figures" / "values"
    if vdir.is_dir():
        for p in vdir.glob("*.tex"):
            defined |= set(re.findall(r"\\pyval(?:text)?\{([^}]*)\}",
                                      p.read_text(encoding="utf8")))
    used = {v for d in docs for v in d.vals}
    for k in sorted(used - defined):
        rep.bad("C7-values", f"\\val{{{k}}} used but no script produces it")
    unused = sorted(defined - used)
    if unused:
        rep.soft("C7-values", f"{len(unused)} computed values are unused: "
                              + ", ".join(unused[:5]))
    if used and not (used - defined):
        rep.good("C7-values", f"{len(used)} value keys, every one produced")


def check_diagram_sources(rep: Report, docs: list[Doc]) -> None:
    keys = {f for d in docs for f in d.figs}
    for k in sorted(keys):
        for lang in LANGS:
            p = ROOT / "figures" / "mermaid" / lang / f"{k}.mmd"
            if not p.is_file():
                rep.bad("C9-diagrams", f"missing {p.relative_to(ROOT)}")
    # And the other way: a source in one language only is a diagram that
    # will print in one edition and fall back to source in the other.
    en = {p.name for p in (ROOT / "figures" / "mermaid" / "en").glob("*.mmd")}
    pl = {p.name for p in (ROOT / "figures" / "mermaid" / "pl").glob("*.mmd")}
    for f in sorted(en ^ pl):
        rep.bad("C9-diagrams", f"figures/mermaid/{f} exists in one language only")


MATH_SPAN = re.compile(r"\$[^$]*\$|\\\[.*?\\\]", re.S)
LISTING_SPAN = re.compile(
    r"\\begin\{(" + "|".join(re.escape(e) for e in LISTING_ENVS) + r")\}.*?\\end\{\1\}",
    re.S)


def check_notation(rep: Report, path: Path) -> None:
    """C10: a decimal point inside maths defeats the locale, and the Polish
    edition wants \\enquote rather than a straight quote."""
    raw = path.read_text(encoding="utf8")
    src = COMMENT_RE.sub("", raw)
    rel = path.relative_to(ROOT)
    listings = list(LISTING_SPAN.finditer(src))

    def in_listing(pos: int) -> bool:
        return any(m.start() <= pos < m.end() for m in listings)

    wrapped = re.compile(r"\\(?:num|val)\{[^{}]*\}")
    for m in MATH_SPAN.finditer(src):
        if in_listing(m.start()):
            continue
        body = wrapped.sub(lambda w: " " * len(w.group(0)), m.group(0))
        for d in re.finditer(r"(?<![\w.\\])\d+\.\d+", body):
            rep.bad("C10-notation",
                    f"{rel}:{src.count(chr(10), 0, m.start())+1} "
                    f"bare decimal {d.group(0)!r} in maths -- wrap it in "
                    f"\\num{{}} or \\val{{}} or the Polish edition prints a "
                    f"full stop where it owes a comma")

    for m in listings:
        for bad in re.finditer(r"\\val(?:text)?\{", m.group(0)):
            rep.bad("C10-notation",
                    f"{rel}:{src.count(chr(10), 0, m.start()+bad.start())+1} "
                    f"\\val inside a verbatim listing does not expand -- "
                    f"use \\transcript{{}} for output written by code/measure")

    if path.parts[-2] == "pl":
        # A straight quote INSIDE \code{} is code, and a Polish quotation mark
        # there would be wrong: \code{if \_\_name\_\_ == "\_\_main\_\_"} is
        # what the reader types. Only prose owes \enquote{}.
        code_spans = [(c.start(), c.end())
                      for c in re.finditer(r"\\code\{[^{}]*\}", src)]
        for m in re.finditer(r'(?<![\\%])"', src):
            if any(a <= m.start() < b for a, b in code_spans):
                continue
            if not in_listing(m.start()):
                rep.soft("C10-notation",
                         f"{rel}:{src.count(chr(10), 0, m.start())+1} "
                         f'straight quote -- use \\enquote{{...}}, which csquotes '
                         f'sets as Polish quotation marks under babel')
                break


NUMBER_RE = re.compile(r"(?<![\w.,])\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")
MACRO_RE = re.compile(r"\\([a-zA-Z@]+)")
# Macros whose count may legitimately differ: they are prose decoration, and a
# good translation uses more or fewer of them.
PROSE_MACROS = {
    "emph", "textbf", "textit", "quad", "qquad", "noindent", "par", "medskip",
    "smallskip", "bigskip", "hfill", "vspace", "mbox", "footnote", "ldots",
    "dots", "text", "dash", "enquote", "-", "textcopyright", "clearpage",
}


def check_numbers(rep: Report, en: Doc, pl: Doc) -> None:
    """C12: every numeric literal, in order, compared STRICTLY.

    The Polish decimal comma is deliberately not normalised away: a number
    localised by hand rather than by \\num{} is a number written twice, and
    only one copy will ever be corrected.
    """
    a = NUMBER_RE.findall(COMMENT_RE.sub("", en.path.read_text(encoding="utf8")))
    b = NUMBER_RE.findall(COMMENT_RE.sub("", pl.path.read_text(encoding="utf8")))
    if a == b:
        rep.good("C12-numbers", f"{en.path.name}: {len(a)} numeric literals identical")
        return
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            rep.bad("C12-numbers",
                    f"{en.path.name}: numeric literal #{i+1} en={x} pl={y}")
            return
    rep.bad("C12-numbers",
            f"{en.path.name}: numeric literal count en={len(a)} pl={len(b)}")


VERB_ENV_RE = re.compile(
    r"\\begin\{(" + "|".join(re.escape(e) for e in LISTING_ENVS) +
    r")\}(?:\[[^\]]*\])?(.*?)\\end\{\1\}", re.S)


def check_verbatim_ascii(rep: Report, path: Path) -> None:
    """C13: listings cannot handle multi-byte UTF-8 in a verbatim body."""
    src = path.read_text(encoding="utf8")
    for m in VERB_ENV_RE.finditer(src):
        for i, ch in enumerate(m.group(2)):
            if ord(ch) > 127:
                line = src.count("\n", 0, m.start(2) + i) + 1
                rep.bad("C13-ascii",
                        f"{path.relative_to(ROOT)}:{line} U+{ord(ch):04X} "
                        f"{ch!r} inside a {m.group(1)} listing")
                return


def check_macro_histogram(rep: Report, en: Doc, pl: Doc) -> None:
    """C14: a macro dropped in translation -- a \\trapbox, an \\index, a
    \\code{} identifier that exists in one edition only."""

    def counts(p: Path) -> Counter:
        c = Counter(MACRO_RE.findall(COMMENT_RE.sub("", p.read_text(encoding="utf8"))))
        for m in PROSE_MACROS:
            c.pop(m, None)
        return c

    ca, cb = counts(en.path), counts(pl.path)
    diffs = [f"\\{k}: en={ca.get(k,0)} pl={cb.get(k,0)}"
             for k in sorted(set(ca) | set(cb)) if ca.get(k, 0) != cb.get(k, 0)]
    if diffs:
        rep.bad("C14-macros", f"{en.path.name}: " + "; ".join(diffs[:6])
                + (f" (+{len(diffs)-6} more)" if len(diffs) > 6 else ""))


SKELETON_RE = re.compile(
    r"\\(input|include|part|appendix|frontmatter|mainmatter|backmatter|"
    r"printindex|tableofcontents)"
    r"(?:\{([^}]*)\})?")


def check_main_files(rep: Report) -> None:
    """C15: every main file reads one shared body, and the body wires up a
    whole book. Exists because a sibling's main file was once rewritten with
    the introduction dropped and every other check passed."""
    seq = {}
    for lang in LANGS:
        name = f"main-{lang}.tex"
        p = ROOT / name
        if not p.is_file():
            rep.bad("C15-mainfiles", f"{name} missing")
            return
        src = COMMENT_RE.sub("", p.read_text(encoding="utf8"))
        seq[name] = [(m.group(1), re.sub(r"/(en|pl)/", "/L/", m.group(2) or ""))
                     for m in SKELETON_RE.finditer(src)]
    ref_name = f"main-{LANGS[0]}.tex"
    ref = seq[ref_name]
    for name, steps in seq.items():
        if ("input", "body") not in steps:
            rep.bad("C15-mainfiles", f"{name} does not \\input{{body}}")
    ok = True
    for name, steps in seq.items():
        if steps == ref:
            continue
        ok = False
        for line in difflib.unified_diff(
                [f"{a} {b}".strip() for a, b in ref],
                [f"{a} {b}".strip() for a, b in steps],
                fromfile=ref_name, tofile=name, lineterm="", n=1):
            if line.startswith(("+", "-")) and not line.startswith(("+++", "---")):
                rep.bad("C15-mainfiles", line)
    if ok:
        rep.good("C15-mainfiles",
                 f"{len(seq)} main files read one shared body ({len(ref)} steps)")
    body = COMMENT_RE.sub("", (ROOT / "body.tex").read_text(encoding="utf8"))
    steps = [(m.group(1), re.sub(r"/(en|pl)/", "/L/", m.group(2) or ""))
             for m in SKELETON_RE.finditer(body)]
    kinds = {a for a, _ in steps}
    missing = {"frontmatter", "mainmatter", "appendix", "backmatter"} - kinds
    if missing:
        rep.bad("C15-mainfiles",
                f"body.tex is missing: {', '.join(sorted(missing))}")
    else:
        rep.good("C15-mainfiles", f"body.tex wires up {len(steps)} steps")


# --------------------------------------------------------------------------

def main() -> int:
    rep = Report()
    pairs = check_filesets(rep)
    check_lang_catalogue(rep)
    check_main_files(rep)

    docs: list[Doc] = []
    for en_p, pl_p in pairs:
        en, pl = tokenise(en_p), tokenise(pl_p)
        docs += [en, pl]
        check_signature(rep, en, pl)
        check_sets(rep, en, pl)
        check_notation(rep, en_p)
        check_notation(rep, pl_p)
        check_numbers(rep, en, pl)
        check_macro_histogram(rep, en, pl)
        check_verbatim_ascii(rep, en_p)
        check_verbatim_ascii(rep, pl_p)

    check_value_defs(rep, docs)
    check_diagram_sources(rep, docs)

    allows = sum(d.allows for d in docs)
    print("=" * 68)
    print("EDITION PARITY")
    print("=" * 68)
    for line in rep.ok:
        print("  ok    " + line)
    for line in rep.warn:
        print("  warn  " + line)
    for line in rep.fail:
        print("  FAIL  " + line)
    print("-" * 68)
    print(f"  {len(pairs)} file pairs | {allows} declared divergences | "
          f"{len(rep.fail)} failures, {len(rep.warn)} warnings")
    return 1 if rep.fail else 0


if __name__ == "__main__":
    sys.exit(main())
