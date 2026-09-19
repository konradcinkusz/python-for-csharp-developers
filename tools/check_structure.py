#!/usr/bin/env python3
"""Structural ledgers for the book: the claims a chapter makes about the
repository, checked against the repository.

Each check answers one question a reader would care about and that nobody can
be trusted to remember:

  --stubs       How many chapters and appendices still print NOT YET WRITTEN,
                per edition, and are the two editions in step about it?
  --listings    Does every \\pyfile, \\csfile and \\pyregion name a file that
                exists under the repository, and does every region marker
                exist in its file? A listing the reader is told to open must
                be there to open.
  --exercises   Does every \\begin{exercise}{key} have its starter, its solution and
                its test under code/exercises/, is the key unique, and does
                its chapter prefix agree with the chapter it sits in?
  --transcripts Does every \\transcript{stem} name a file under
                figures/transcripts/? The macro's own fallback prints a grey
                marker and BUILDS, which is how a sibling book shipped ten
                listings that never reached a page.
  --lines       Is every line of every .py file under code/ at most 79
                columns? A longer line does not overfull -- listings wraps it
                silently and prints an arrow into the middle of what the
                reader will paste into an editor.
  --pins        Do the versions in preamble.tex agree with the `==` pins in
                code/pyproject.toml? Two copies of one fact, and only one of
                them is what CI installs.
  --words       Is every WRITTEN chapter under its word budget from
                tools/chapters.json? Prose words only: listings, comments and
                macro names do not count. This is the book's hard frame.
  --csbox       How many "In C# terms" boxes each written chapter carries.
                REPORTED, NEVER FATAL: a chapter with none has stopped
                translating, but there is no defensible threshold.

Exit code is 0 when the ledger is clean and 1 when it is not. --soft turns a
failing check into a report.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANGS = ("en", "pl")
COLUMNS = 79

RE_STUB = re.compile(r"\\chapterstub\{")
RE_COMMENT = re.compile(r"(?<!\\)%.*$", re.M)
RE_PYFILE = re.compile(r"\\(?:pyfile|csfile)\{([^}]*)\}")
RE_PYREGION = re.compile(r"\\pyregion\{([^}]*)\}\{([^}]*)\}")
RE_TRANSCRIPT = re.compile(r"\\transcript\{([^}]*)\}")
RE_EXERCISE = re.compile(r"\\begin\{exercise\}\{([^}]*)\}")
# The macro form the environment replaced. It no longer exists, and a chapter
# that uses it would otherwise be an exercise this check cannot see.
RE_OLD_EXERCISE = re.compile(r"\\exercise\{")
RE_CSBOX = re.compile(r"\\begin\{csbox\}")
RE_CHAPTER_FILE = re.compile(r"^ch(\d\d)-")
# Only the pinned block: a macro whose name ends in "ver", whose body is a
# version, and whose trailing comment is the distribution name. \pyver and
# \pypatch are Python itself and are compared with code/.python-version.
RE_PIN_TEX = re.compile(
    r"\\newcommand\{\\(\w+ver)\}\{(\d[\w.]*)\}\s*%\s*([A-Za-z0-9_.-]+)\s*$",
    re.M,
)
RE_PIN_TOML = re.compile(r'"([A-Za-z0-9_.-]+)==([^"]+)"')

LISTING_ENVS = ("python", "csharp", "shellcmd", "tomlcode", "yamlcode",
                "jsoncode", "console", "lstlisting", "verbatim")


def manifest() -> dict:
    return json.loads((ROOT / "tools" / "chapters.json").read_text(encoding="utf8"))


def tex_files(tree: str, lang: str) -> list[Path]:
    d = ROOT / tree / lang
    return sorted(d.glob("*.tex")) if d.is_dir() else []


def written(text: str) -> bool:
    # Comment-stripped: the stub header this repo's generator writes NAMES
    # the macro in prose, so a raw search for \chapterstub{ is true of every
    # stub forever, even one whose block has been deleted and replaced with a
    # written chapter that (as instructed) kept the header comment above it.
    # gen_stubs.py's written() carries the same fix and the same reasoning.
    return not RE_STUB.search(RE_COMMENT.sub("", text))


def result(name: str, problems: list[str], soft: bool, ok_msg: str) -> int:
    if problems:
        for p in problems:
            print(f"  {'WARN' if soft else 'FAIL'}  {p}")
        print(f"  {name}: {len(problems)} problem(s)")
        return 0 if soft else 1
    print(f"  {ok_msg}")
    return 0


# ---------------------------------------------------------------------------

def check_stubs(soft: bool) -> int:
    problems = []
    for tree in ("chapters", "appendices"):
        counts = {}
        for lang in LANGS:
            files = tex_files(tree, lang)
            stubs = [p.name for p in files if not written(p.read_text(encoding="utf8"))]
            counts[lang] = set(stubs)
            print(f"  {lang}: {len(stubs)} of {len(files)} {tree} are stubs")
        if counts["en"] != counts["pl"]:
            problems.append(f"{tree}: stubs differ between editions: "
                            f"{sorted(counts['en'] ^ counts['pl'])}")
    return result("stubs", problems, soft, "both editions agree about what is written")


def check_listings(soft: bool) -> int:
    problems, seen = [], 0
    for tree in ("frontmatter", "chapters", "appendices"):
        for lang in LANGS:
            for p in tex_files(tree, lang):
                src = RE_COMMENT.sub("", p.read_text(encoding="utf8"))
                rel = p.relative_to(ROOT)
                for m in RE_PYFILE.finditer(src):
                    seen += 1
                    if not (ROOT / m.group(1)).is_file():
                        problems.append(f"{rel}: listing file missing: {m.group(1)}")
                for m in RE_PYREGION.finditer(src):
                    seen += 1
                    path, region = m.group(1), m.group(2)
                    f = ROOT / path
                    if not f.is_file():
                        problems.append(f"{rel}: listing file missing: {path}")
                        continue
                    body = f.read_text(encoding="utf8")
                    for marker in (f"--8<-- [start:{region}]", f"--8<-- [end:{region}]"):
                        if marker not in body:
                            problems.append(f"{rel}: {path} has no `{marker}`")
    return result("listings", problems, soft,
                  f"{seen} listing references, every file and region present")


def check_transcripts(soft: bool) -> int:
    problems, seen = [], 0
    for tree in ("frontmatter", "chapters", "appendices"):
        for lang in LANGS:
            for p in tex_files(tree, lang):
                src = RE_COMMENT.sub("", p.read_text(encoding="utf8"))
                for m in RE_TRANSCRIPT.finditer(src):
                    seen += 1
                    stem = m.group(1)
                    if "/" in stem or stem.endswith(".txt"):
                        problems.append(f"{p.relative_to(ROOT)}: \\transcript takes a "
                                        f"stem, not a path: {stem!r}")
                    elif not (ROOT / "figures" / "transcripts" / f"{stem}.txt").is_file():
                        problems.append(f"{p.relative_to(ROOT)}: no transcript "
                                        f"figures/transcripts/{stem}.txt (run make numbers)")
    return result("transcripts", problems, soft,
                  f"{seen} transcript references, every file present")


def check_exercises(soft: bool) -> int:
    problems, keys = [], {}
    for tree in ("frontmatter", "chapters", "appendices"):
        for p in tex_files(tree, "en"):
            src = RE_COMMENT.sub("", p.read_text(encoding="utf8"))
            m = RE_CHAPTER_FILE.match(p.name)
            chap = m.group(1) if m else ("00" if tree == "frontmatter" else None)
            for e in RE_OLD_EXERCISE.finditer(src):
                problems.append(f"{p.relative_to(ROOT)}: \\exercise{{...}} is the old macro "
                                f"form; write \\begin{{exercise}}{{key}}{{title}} ... "
                                f"\\end{{exercise}}")
            for e in RE_EXERCISE.finditer(src):
                key = e.group(1)
                rel = p.relative_to(ROOT)
                if key in keys:
                    problems.append(f"{rel}: exercise key {key!r} already used in {keys[key]}")
                keys[key] = rel
                if not re.fullmatch(r"e\d\d_\d\d_[a-z0-9_]+", key):
                    problems.append(f"{rel}: exercise key {key!r} is not eNN_MM_name")
                    continue
                if chap is None:
                    problems.append(f"{rel}: an exercise in an appendix has no "
                                    f"chapter directory to live in")
                    continue
                if key[1:3] != chap:
                    problems.append(f"{rel}: exercise {key!r} sits in chapter {chap}")
                d = ROOT / "code" / "exercises" / f"ch{chap}"
                for f in (d / f"{key}.py", d / "solutions" / f"{key}.py",
                          d / f"test_{key}.py"):
                    if not f.is_file():
                        problems.append(f"{rel}: {key}: missing {f.relative_to(ROOT)}")
    return result("exercises", problems, soft,
                  f"{len(keys)} exercises, each with a starter, a solution and a test")


def check_lines(soft: bool) -> int:
    # .cs as well as .py: Appendix D prints its C# solutions through \csfile,
    # so they are listings and the page does not care which language they are
    # in. bin/ and obj/ hold generated sources nobody wrote and nothing
    # prints, so they are skipped the way .venv is.
    problems, n = [], 0
    skip = {".venv", "bin", "obj"}
    files = sorted((ROOT / "code").rglob("*.py")) + \
        sorted((ROOT / "code").rglob("*.cs"))
    for p in sorted(files):
        if skip & set(p.parts):
            continue
        n += 1
        for i, line in enumerate(p.read_text(encoding="utf8").splitlines(), start=1):
            if len(line) > COLUMNS:
                problems.append(f"{p.relative_to(ROOT)}:{i} is {len(line)} columns")
    return result("lines", problems, soft, f"{n} code files, no line over {COLUMNS} columns")


def check_pins(soft: bool) -> int:
    tex = (ROOT / "preamble.tex").read_text(encoding="utf8")
    tex_pins = {dist: ver for _, ver, dist in RE_PIN_TEX.findall(tex)}
    toml = (ROOT / "code" / "pyproject.toml").read_text(encoding="utf8")
    toml_pins = dict(RE_PIN_TOML.findall(toml))
    problems = []
    for dist, ver in sorted(toml_pins.items()):
        if dist not in tex_pins:
            problems.append(f"code/pyproject.toml pins {dist}=={ver} and preamble.tex "
                            f"has no macro for it")
        elif tex_pins[dist] != ver:
            problems.append(f"{dist}: preamble.tex says {tex_pins[dist]}, "
                            f"code/pyproject.toml says {ver}")
    for dist, ver in sorted(tex_pins.items()):
        if dist not in toml_pins and dist not in ("uv", "dotnet"):
            problems.append(f"preamble.tex pins {dist} {ver} and code/pyproject.toml "
                            f"does not install it")
    pyv = (ROOT / "code" / ".python-version").read_text(encoding="utf8").strip()
    m = re.search(r"\\newcommand\{\\pypatch\}\{([^}]*)\}", tex)
    if not m or m.group(1) != pyv:
        problems.append(f"Python: preamble.tex says {m.group(1) if m else '?'}, "
                        f"code/.python-version says {pyv}")
    # uv is not in pyproject.toml -- it installs pyproject.toml -- so its pin
    # lives in the preamble and in every workflow's setup-uv step. Three
    # workflows carried the same string by hand and nothing compared them.
    uv_ci = 0
    for wf in sorted((ROOT / ".github" / "workflows").glob("*.yml")):
        for w in re.findall(r'^\s*version:\s*"([^"]+)"', wf.read_text(encoding="utf8"),
                            flags=re.M):
            uv_ci += 1
            if w != tex_pins.get("uv"):
                problems.append(f"{wf.relative_to(ROOT)} installs uv {w}; preamble.tex "
                                f"pins {tex_pins.get('uv', '?')}")
    # .NET is a tool too, and it is pinned in ONE place on purpose:
    # code/csharp/global.json. The workflow reads that file rather than
    # carrying the version again, which is the defect uv's pin had. So the
    # only comparison owed is preamble.tex against global.json -- plus a
    # check that no workflow has quietly reintroduced a second copy.
    gj = ROOT / "code" / "csharp" / "global.json"
    dotnet_ci = 0
    if gj.exists():
        declared = json.loads(gj.read_text(encoding="utf8"))["sdk"]["version"]
        if declared != tex_pins.get("dotnet"):
            problems.append(f"code/csharp/global.json pins .NET {declared}; "
                            f"preamble.tex says {tex_pins.get('dotnet', '?')}")
        for wf in sorted((ROOT / ".github" / "workflows").glob("*.yml")):
            text = wf.read_text(encoding="utf8")
            dotnet_ci += len(re.findall(r"^\s*global-json-file:", text, flags=re.M))
            for v in re.findall(r'^\s*dotnet-version:\s*"?([^"\s]+)"?', text, flags=re.M):
                problems.append(f"{wf.relative_to(ROOT)} names .NET {v} directly; "
                                f"point setup-dotnet at code/csharp/global.json "
                                f"instead, so the pin stays in one place")
    return result("pins", problems, soft,
                  f"{len(toml_pins)} pins agree between preamble.tex and pyproject.toml; "
                  f"uv {tex_pins.get('uv', '?')} in preamble.tex and {uv_ci} workflow step(s); "
                  f".NET {tex_pins.get('dotnet', '?')} in preamble.tex, global.json and "
                  f"{dotnet_ci} workflow step(s)")


def prose_words(src: str) -> int:
    """Words a reader reads: no comments, no listings, no macro names."""
    s = RE_COMMENT.sub("", src)
    for env in LISTING_ENVS:
        s = re.sub(r"\\begin\{%s\}.*?\\end\{%s\}" % (re.escape(env), re.escape(env)),
                   " ", s, flags=re.S)
    s = re.sub(r"\$[^$]*\$", " ", s)
    s = re.sub(r"\\(?:pyfile|csfile|pyregion|mermaidfig|transcript|label|ref|index)"
               r"(?:\{[^{}]*\})+", " ", s)
    s = re.sub(r"\\[A-Za-z@]+\*?", " ", s)
    s = re.sub(r"[{}\[\]&\\~]", " ", s)
    return len([w for w in s.split() if re.search(r"[A-Za-z0-9\u00C0-\u017F]", w)])


def check_words(soft: bool) -> int:
    budgets = {c["file"]: int(c["words"]) for c in manifest()["chapters"]}
    problems, rows = [], []
    for lang in LANGS:
        for p in tex_files("chapters", lang):
            src = p.read_text(encoding="utf8")
            if not written(src):
                continue
            n = prose_words(src)
            budget = budgets.get(p.stem, 3000)
            rows.append((lang, p.stem, n, budget))
            if n > budget:
                problems.append(f"chapters/{lang}/{p.name}: {n} words against a budget "
                                f"of {budget}")
    for lang, stem, n, budget in rows:
        print(f"  {lang} {stem:28} {n:5} / {budget}")
    if not rows:
        print("  no written chapters yet")
    return result("words", problems, soft, "every written chapter is inside its budget")


def check_csbox(soft: bool) -> int:
    for p in tex_files("chapters", "en"):
        src = p.read_text(encoding="utf8")
        if not written(src):
            continue
        print(f"  {p.stem:28} {len(RE_CSBOX.findall(src))} csbox")
    print("  (reported, never fatal)")
    return 0


def check_traps(soft: bool) -> int:
    """Appendix B against notes/02-traps.md, which is the authority.

    Three things nothing else can see. The catalogue must carry no
    duplicate number, because an entry is cited BY number and a collision
    breaks the one thing the numbering exists for -- six parallel branches
    produced three collisions before this check existed. Both editions'
    Appendix B must print exactly the catalogue's entries, so a trap added
    to the notes and not to the book, or dropped from one edition, fails
    here rather than reaching a reader. And every entry must name a
    chapter, because an entry no chapter elicits is a defect in the
    catalogue rather than a fact about the book.

    Numbers are language-independent, which is what lets one check cover
    both editions; parity compares the prose around them.
    """
    notes = (ROOT / "notes" / "02-traps.md").read_text(encoding="utf8")
    rows = re.findall(r"^\| (\d+) \|(.*)$", notes, flags=re.M)
    problems = []

    seen: dict[str, int] = {}
    for num, _ in rows:
        seen[num] = seen.get(num, 0) + 1
    for num, n in sorted(seen.items(), key=lambda kv: int(kv[0])):
        if n > 1:
            problems.append(f"notes/02-traps.md: entry {num} appears {n} times; "
                            f"a number is cited and is never reused")

    for num, body in rows:
        if not re.search(r"\bCh\. \d+", body):
            problems.append(f"notes/02-traps.md: entry {num} names no chapter")

    catalogue = {n for n, _ in rows}
    for lang in LANGS:
        src = (ROOT / "appendices" / lang / "appB-traps.tex")
        if not src.exists() or not written(src.read_text(encoding="utf8")):
            continue
        printed = set(re.findall(r"\\trapentry\{(\d+)\}",
                                 src.read_text(encoding="utf8")))
        for num in sorted(catalogue - printed, key=int):
            problems.append(f"appendices/{lang}/appB-traps.tex: entry {num} is in "
                            f"the catalogue and not in the appendix")
        for num in sorted(printed - catalogue, key=int):
            problems.append(f"appendices/{lang}/appB-traps.tex: entry {num} is in "
                            f"the appendix and not in the catalogue")
    return result("traps", problems, soft,
                  f"{len(catalogue)} trap entries, each numbered once and naming a "
                  f"chapter, and every one printed in both editions")


def check_cheatsheet(soft: bool) -> int:
    """Appendix A's chapter references against the chapters.

    Every row of the cheat sheet names the chapter that teaches it, which
    makes every row a claim about the book -- and an appendix is the class
    of claim nothing else gates. This checks the half a machine can: that
    each \\ref names a label some chapter actually defines, and that the
    chapter is WRITTEN rather than still a stub, since a row pointing at a
    stub promises something no reader can go and read.

    The other half stays a reading job and cannot be automated: whether the
    row is TRUE of that chapter. The count printed here is what the author
    has to re-read, and it is printed for that reason.
    """
    labels: dict[str, str] = {}
    for lang in LANGS:
        for p in tex_files("chapters", lang):
            src = p.read_text(encoding="utf8")
            for lab in re.findall(r"\\label\{(ch:[^}]+)\}", RE_COMMENT.sub("", src)):
                labels[lab] = p.stem
    stubs = {p.stem for p in tex_files("chapters", "en")
             if not written(p.read_text(encoding="utf8"))}

    problems, rows = [], 0
    for lang in LANGS:
        src = ROOT / "appendices" / lang / "appA-cheatsheet.tex"
        if not src.exists():
            continue
        text = RE_COMMENT.sub("", src.read_text(encoding="utf8"))
        if not written(text):
            continue
        refs = re.findall(r"\\ref\{(ch:[^}]+)\}", text)
        rows += len(refs)
        for ref in refs:
            if ref not in labels:
                problems.append(f"appendices/{lang}/appA-cheatsheet.tex: a row "
                                f"points at {ref}, which no chapter defines")
            elif labels[ref] in stubs:
                problems.append(f"appendices/{lang}/appA-cheatsheet.tex: a row "
                                f"points at {ref}, whose chapter is still a stub")
    return result("cheatsheet", problems, soft,
                  f"{rows} cheat-sheet rows across both editions, every one naming a "
                  f"chapter that exists and is written "
                  f"({len(set(labels))} chapter labels); whether each row is TRUE of "
                  f"its chapter is a reading job and is not checked here")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    for name in ("stubs", "listings", "exercises", "transcripts", "lines", "pins",
                 "words", "csbox", "traps", "cheatsheet", "all"):
        ap.add_argument(f"--{name}", action="store_true")
    ap.add_argument("--soft", action="store_true", help="report instead of failing")
    a = ap.parse_args()
    checks = {
        "stubs": check_stubs, "listings": check_listings, "exercises": check_exercises,
        "transcripts": check_transcripts, "lines": check_lines, "pins": check_pins,
        "words": check_words, "csbox": check_csbox, "traps": check_traps,
        "cheatsheet": check_cheatsheet,
    }
    chosen = [k for k in checks if getattr(a, k)] or (list(checks) if a.all else [])
    if not chosen:
        ap.print_help()
        return 2
    rc = 0
    for k in chosen:
        print(f"== {k} ==")
        rc |= checks[k](a.soft)
    return rc


if __name__ == "__main__":
    sys.exit(main())
