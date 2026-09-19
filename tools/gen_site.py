#!/usr/bin/env python3
"""Assemble the Pages site, filling the one-pager's facts from the tree.

The summary page at
https://konradcinkusz.github.io/python-for-csharp-developers/ is the first
thing anybody reads about this book, and every fact on it -- how many
chapters are written, what the parts are, how many exercises ship -- is a
fact this repository already computes for Appendix E. A page that repeats
them by hand is a second copy of every one of those numbers, kept in a file
no gate reads.

It went stale exactly that way: the committed page announced itself as a
scaffold, and said in as many words that nothing on it was a chapter you
could learn from, for as long as it took thirteen chapters to be written.
Nothing failed, because nothing was watching.

So the page is a TEMPLATE, `docs/index.html.in`, and this script renders it:
every count comes from `figures/values/ledgers.tex` -- the file
`code/measure/ledgers.py` writes and `make verify` drift-gates -- and the
contents table is generated from `tools/chapters.json`, which is the same
manifest the book's own chapter sequence is generated from. A chapter
written, renamed or added moves the page on the next build and no one has
to remember.

The rendered site is build output and is not committed: there is nothing to
drift, so this needs no gate of its own beyond `--check`, which renders into
a temporary directory and fails on an unresolved placeholder. That is cheap
enough to sit beside the other source gates, and it is what stops a broken
template being discovered only after a push to `main` -- pages.yml is the
only workflow that runs this, and it runs on `main` alone.

  python3 tools/gen_site.py _site     # assemble, PDFs copied in separately
  python3 tools/gen_site.py --check   # render and throw it away
"""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sys
import tempfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
LEDGERS = ROOT / "figures" / "values" / "ledgers.tex"
MANIFEST = ROOT / "tools" / "chapters.json"

# The same two expressions ledgers.py counts stubs with, and for the same
# reason: the generated stub header NAMES \chapterstub in a sentence of
# prose, so a raw substring search calls a written chapter a stub forever.
# Comments are stripped before the test. All the tools that decide what
# "written" means must agree, or the page and Appendix E describe different
# books.
RE_STUB = re.compile(r"\\chapterstub\{")
RE_COMMENT = re.compile(r"(?<!\\)%.*$", re.M)
RE_PYVAL = re.compile(r"\\pyval\{([^}]*)\}\{([^}]*)\}")
RE_PLACEHOLDER = re.compile(r"\{\{([a-zA-Z0-9_.]+)\}\}")

LANGS = ("en", "pl")


def ledger_values() -> dict[str, str]:
    """Read the committed ledger file rather than recounting the tree.

    ledgers.py is the definition of every one of these quantities and it is
    drift-gated; recounting here would be a second implementation to
    disagree with it on an edge case, which is how a ledger starts lying.
    """
    if not LEDGERS.exists():
        raise SystemExit(
            f"{LEDGERS.relative_to(ROOT)} is missing: run `make numbers` "
            f"(or `cd code && uv run python measure/ledgers.py`) first"
        )
    text = LEDGERS.read_text(encoding="utf8")
    values = {k: v for k, v in RE_PYVAL.findall(text)}
    if not values:
        raise SystemExit(f"{LEDGERS.relative_to(ROOT)} defines no \\pyval")
    return values


def written(tree: str, file: str) -> bool:
    """True when both editions of this file are written, asserting they agree.

    A chapter written in one language and a stub in the other is a defect
    parity catches; here it would print a marker true of neither edition, so
    it stops the build rather than picking one.
    """
    states: dict[str, bool] = {}
    for lang in LANGS:
        path = ROOT / tree / lang / f"{file}.tex"
        if not path.exists():
            raise SystemExit(f"{path.relative_to(ROOT)}: named in the manifest, not on disk")
        body = RE_COMMENT.sub("", path.read_text(encoding="utf8"))
        states[lang] = not RE_STUB.search(body)
    if states["en"] != states["pl"]:
        raise SystemExit(
            f"{tree}/{file}: written in one edition and a stub in the other "
            f"(en={states['en']}, pl={states['pl']})"
        )
    return states["en"]


def esc(text: str) -> str:
    return html.escape(text, quote=False)


def contents_table(manifest: dict[str, object]) -> str:
    """The parts, their chapters and which of them are written.

    Generated from the manifest that generates the book's own chapter
    sequence, so the page cannot describe a different book from the PDF
    beside it.
    """
    chapters = {c["id"]: c for c in manifest["chapters"]}
    rows: list[str] = []
    for part in manifest["parts"]:
        items = []
        for cid in part["ids"]:
            ch = chapters[cid]
            done = written("chapters", ch["file"])
            cls = "done" if done else "todo"
            mark = "written" if done else "planned"
            items.append(
                f'      <li class="{cls}">'
                f'<span class="num">{esc(cid)}</span> {esc(ch["en"])}'
                f'<span class="mark">{mark}</span></li>'
            )
        rows.append(
            "  <tr>\n"
            f'    <th scope="row">{esc(part["en"])}'
            f'<span class="rel">{esc(part["release"])}</span></th>\n'
            "    <td>\n      <ul class=\"chapters\">\n"
            + "\n".join(items)
            + "\n      </ul>\n    </td>\n  </tr>"
        )
    return "\n".join(rows)


def appendix_list(manifest: dict[str, object]) -> str:
    items = []
    for app in manifest["appendices"]:
        done = written("appendices", app["file"])
        cls = "done" if done else "todo"
        mark = "written" if done else "planned"
        items.append(
            f'  <li class="{cls}"><span class="num">{esc(app["id"])}</span> '
            f'{esc(app["en"])}<span class="mark">{mark}</span></li>'
        )
    return "\n".join(items)


def substitutions() -> dict[str, str]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf8"))
    led = ledger_values()

    def n(key: str) -> str:
        if key not in led:
            raise SystemExit(f"{LEDGERS.relative_to(ROOT)} has no {key}")
        return led[key]

    appendices_total = int(n("ledger.appendices.total"))
    appendices_stubs = int(n("ledger.appendices.stubs"))
    # ledgers.py counts one language's .mmd sources and asserts the other
    # matches, so this is already the per-edition figure -- which is what a
    # reader holds. Do not double it to describe the repository.
    diagrams_total = int(n("ledger.diagrams"))

    values = {
        "chapters.total": n("ledger.chapters.total"),
        "chapters.written": n("ledger.chapters.written"),
        "chapters.stubs": n("ledger.chapters.stubs"),
        "appendices.total": str(appendices_total),
        "appendices.written": str(appendices_total - appendices_stubs),
        "exercises": n("ledger.exercises"),
        "listings": n("ledger.listings"),
        "diagrams": str(diagrams_total),
        "verifybox": n("ledger.verifybox"),
        "contents": contents_table(manifest),
        "appendices.list": appendix_list(manifest),
        "generated": date.today().isoformat(),
    }
    return values


def render(text: str, values: dict[str, str], where: str) -> str:
    missing: list[str] = []

    def one(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in values:
            missing.append(key)
            return match.group(0)
        return values[key]

    out = RE_PLACEHOLDER.sub(one, text)
    if missing:
        raise SystemExit(
            f"{where}: no value for {', '.join(sorted(set(missing)))}. "
            f"Known keys: {', '.join(sorted(values))}"
        )
    return out


def assemble(out_dir: Path) -> int:
    values = substitutions()
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    rendered = 0
    copied = 0
    for src in sorted(DOCS.rglob("*")):
        if src.is_dir():
            continue
        rel = src.relative_to(DOCS)
        if src.suffix == ".in":
            dest = out_dir / rel.with_suffix("")
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(
                render(src.read_text(encoding="utf8"), values, str(rel)),
                encoding="utf8",
            )
            rendered += 1
        else:
            dest = out_dir / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            copied += 1

    if not (out_dir / "index.html").exists():
        raise SystemExit("docs/ produced no index.html: the site has no front page")

    print(
        f"  {rendered} template(s) rendered, {copied} file(s) copied "
        f"into {out_dir}"
    )
    print(
        f"  {values['chapters.written']} of {values['chapters.total']} chapters, "
        f"{values['appendices.written']} of {values['appendices.total']} appendices, "
        f"{values['exercises']} exercises, {values['listings']} listings"
    )
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("out", nargs="?", default="_site", help="output directory")
    ap.add_argument(
        "--check",
        action="store_true",
        help="render into a temporary directory and discard it",
    )
    args = ap.parse_args()

    if args.check:
        with tempfile.TemporaryDirectory() as tmp:
            assemble(Path(tmp) / "site")
        print("  gen_site: template renders, every placeholder resolved")
        return 0
    return assemble(ROOT / args.out if not Path(args.out).is_absolute() else Path(args.out))


if __name__ == "__main__":
    sys.exit(main())
