# CLAUDE.md — working on this book

Context for continuing *Python for .NET Engineers* / *Python dla inżynierów
.NET*. Read this before touching a chapter.

This repository is the third of a trilogy and inherits its rules from the
other two: the LaTeX pipeline and the chapter conventions from
[llm-book](https://github.com/konradcinkusz/llm-book), the bilingual
single-source wiring and the gates from
[math-for-ai-engineers](https://github.com/konradcinkusz/math-for-ai-engineers).
Where a rule below says *inherited*, the reasoning that earned it is in that
repository's `CLAUDE.md`, and it is not repeated here.

---

## Status

| | Done | Remaining |
|---|---|---|
| Structure | `body.tex` read by both main files, shared preamble, generated `structure.tex`, Makefile, CI, parity tooling, Mermaid pipeline, exercise mechanism | — |
| Front matter | Title page, copyright, *How to use this book*, Introduction — **both editions** | — |
| Chapters | **0 of 14 written.** Every chapter is a brief printed where the chapter will go | all fourteen |
| Appendices | **E (Manifest), generated.** A–D are briefs | A, B, C, D |
| Code | `code/` is a locked uv project: the `trace-assert` skeleton, the first listing, the first exercise, the two measurement scripts, and CI runs all of it | every chapter's listings and exercises; the eight experiments |

**This is the scaffold.** It exists so that the shape of the book can be
argued with before Chapter 1 is written, and so that the first chapter is
written into a build that already has every gate. Nothing in it teaches
Python yet.

**Two editions, one paper size, both clean.** A4 at 12pt, single-sided, the
format the book is read in — there is no print format and there will not be
one.

| | Pages | Errors | Unresolved | Overfull hbox | Overfull vbox |
|---|---|---|---|---|---|
| `main-en` | 37 | 0 | 0 | 0 | 0 |
| `main-pl` | 37 | 0 | 0 | 0 | 0 |

**Re-measure both rows from the build in front of you** after any change; a
page count carried across a layout change is the first thing in this file
to go stale.

**Debt ledgers, reported by CI on every build** (`make debt`), and printed
for the reader in Appendix E, which `code/measure/ledgers.py` computes from
the tree so that `make verify` fails when a ledger moves and the appendix
does not:

- **14 of 14 chapters are stubs, in each edition; 4 of 5 appendices are**,
  and both editions agree about what is written
- 2 listing references, every file and region present · 1 exercise, with a
  starter, a solution and a test · 2 transcript references, every file
  present · 14 code files, none over 79 columns · 19 pins agree between
  `preamble.tex` and `code/pyproject.toml`
- **0 `verifybox` blocks.** Keep it that way: a box is a promise to the
  reader that something was not run
- 4 Mermaid sources, two per language, all rendering, both placed
- 9 computed value keys, every one produced and every one used
- Parity: 23 file pairs, 0 failures, 0 warnings · 26 labels in each edition,
  0 mismatches
- **8 experiments specified, all free. The Status column in
  `notes/01-curriculum.md` §4 is the ledger**, filled in by the pass that
  runs each one; neither that file nor this one states a total, because a
  count of how many have run is the class of claim that decays silently

---

## Non-negotiable conventions

**Verify before writing.** Do not write API surface from memory. The pinned
versions are recent enough that a model's recollection of pydantic, FastAPI,
SQLAlchemy or pytest is a description of an older major. Sources, in order
of authority:

1. **The installed package.** `cd code && uv run python -c "import x; ..."`
   against the locked environment, or a scratch venv
   (`uv venv scratch && VIRTUAL_ENV=scratch uv pip install pkg==pin`) for
   anything not in `pyproject.toml`. This is the only source that cannot be
   stale.
2. The project's repository at the tag matching the pin; tests and examples
   before prose.
3. The project's documentation, written for the happy path.
4. PyPI release metadata, for dates.

> **Network note.** In the Claude Code web sandbox `pypi.org`,
> `files.pythonhosted.org` and `archive.ubuntu.com` are reachable; Ubuntu
> PPAs answer 403 through the proxy and `api.github.com` needs `add_repo`.
> `tools/check_versions.py` compares every pin against PyPI; run it before
> starting a chapter, and resolve a pin that has drifted far rather than
> writing against a version nobody will install.

**Run listings, or mark them.** Every listing is a file under `code/`,
pulled in with `\pyfile{}` or `\pyregion{}`, and `code/tests/test_listings.py`
runs every `chNN/*.py` as a script on every push. Anything that is not run
that way goes inside `\begin{verifybox}`. Removing a verifybox means you ran
the code — not that you reread it and it felt right. Nothing ships to a
reader with one attached.

**An exercise is three files, and the starter must fail.** `\exercise{key}
{title}{body}` in the prose is tied to `code/exercises/chNN/<key>.py` (the
starter the reader opens), `code/exercises/chNN/solutions/<key>.py` (what
CI runs), and `code/exercises/chNN/test_<key>.py`. `make code` runs the
solutions with `PYBOOK_SOLUTIONS=1`; `make starters` runs the starters with
`PYBOOK_STARTERS=fail`, under which `code/exercises/conftest.py` marks every
test strict-xfail — so a starter that accidentally passes is a build
failure, and so is a solution that fails. `check_structure.py --exercises`
refuses an `\exercise{}` whose three files are not all there, and an
exercise key must carry its chapter's number (`e07_02_...` in Chapter 7,
`e00_...` in the front matter). That triple is what makes *PDF on the left,
IDE on the right* a checked claim rather than a hope.

**Every number is computed, not remembered.** A numeric value that a reader
cannot do in their head goes in a script under `code/measure/`, is written
to `figures/values/<name>.tex` as `\pyval{key}{value}`, and reaches the page
as `\val{key}`. A console transcript is a computed number that happens to be
verbatim: `code/measure/transcripts.py` writes `figures/transcripts/<stem>.txt`
and the page pulls it in with `\transcript{stem}`. Both directories are
**committed**, so a changed number shows up in review as a diff, and `make
verify` fails when a script no longer produces what the book prints. **A
`\val{}` inside a listing does not expand** — `listings` is verbatim — which
is what transcripts are for, and parity's C10 refuses the attempt.
`figures/values/all.tex` is the index the preamble `\input`s; it is
regenerated by `make numbers` and by CI and is gitignored.

**Versions live in two places, and a gate keeps them in step.**
`preamble.tex` carries every pin as a macro (`\pydanticver`, `\pytestver`,
and the rest — each followed by a `% <distribution>` comment, which is what
the gate reads), and `code/pyproject.toml` carries the same pins as `==`
requirements, because uv needs them there. `check_structure.py --pins`
fails when the two disagree, and compares `\pypatch` with
`code/.python-version`. Never write a version number into a chapter; a
chapter says `\pydanticver`.

**79 columns.** Every code file under `code/` and every transcript is held
to 79 columns by `check_structure.py --lines` and by the transcript writer's
own guard. Measured on this layout: a listing line fits the measure at
`\footnotesize` up to **89 columns and overflows at 90**, so ruff's limit
leaves ten columns of slack and no listing line will ever produce an
overfull box. That slack is deliberate and is not to be spent on a wider
ruff limit.

**Under 3,000 words of prose per chapter.** `check_structure.py --words`
counts what a reader reads — no comments, no listings, no macro names — and
fails a written chapter that is over the budget in the manifest. Listings
and exercises are not prose. A chapter that is mostly listings is what this
book wants.

**Two to four figures per chapter**, Mermaid, one source per language under
`figures/mermaid/{en,pl}/<key>.mmd`, committed. Renders are build output and
are gitignored. **ASCII only inside `.mmd` files**, because the unrendered
fallback typesets the source through `listings`. A figure may not answer a
question the prose beside it puts to the reader (inherited, and the reason
is in the math book's *rule 2*).

**ASCII inside listings.** No em-dashes, no smart quotes, no non-breaking
spaces in `python`, `csharp`, `shellcmd`, `tomlcode`, `yamlcode`,
`jsoncode`, `console`. The preamble maps the Polish diacritics and the
common dashes; nothing else is safe, and **never add a `literate` mapping
for U+00A0** (inherited; fatal, and the message names neither the character
nor the line).

**Underscores** inside `\code{}`, `\api{}` and `\pkg{}` must be written
`\_`. Python is full of them and this is the single most common way to
break the build. In a chapter title use `\texorpdfstring`.

**No instruction may depend on where the page breaks.** *Before you read
on*, never *before you turn over*: the two editions paginate differently by
construction.

**Voice.** British English and idiomatic Polish, second person, senior
audience. The book may say a Python idiom is worse than the C# one, that a
popular library is not worth its cost, and that the author has not verified
something. No marketing register. No *simply*, no *just*, no *powerful*.

**Prefer measurements to assertions.** Eight experiments are specified, all
free; until one runs, the claim it would support is labelled as judgement.
The two methodological errors the LangChain book made running its service
benchmark (load driver and server on one event loop; a client that
saturated before the server) are the first two things to check before E5 is
believed.

---

## Two editions, one source

Two main files that differ in five lines and share everything else,
including the document body:

```
main-{en,pl}.tex       \documentclass[12pt,oneside,openany]{book}, \booklang, the PDF title
body.tex               THE document body. One copy, read by both.
preamble.tex           all machinery, and the pinned versions
lang/en.tex            every user-visible string
lang/pl.tex            the same macro set, or C3 fails
structure.tex          GENERATED chapter sequence, from tools/chapters.json
structure-appendices.tex  GENERATED appendix sequence
chapters/{en,pl}/      the only place prose is duplicated
appendices/{en,pl}/
frontmatter/{en,pl}/
```

`body.tex` is C15 made structural (inherited): every main file reads the
body, and the body still wires up a whole book, so a main file cannot be
rewritten with the introduction dropped.

**The generator owns the sequence.** `tools/gen_stubs.py` writes every stub
and both structure files from `tools/chapters.json`. It never overwrites a
written file (one with no `\chapterstub{}` left in it), it refuses outright
when a written file has been dropped from the manifest, and `--check` fails
when anything is stale. Chapter and appendix **titles pass through
`title()`**, which escapes `#`, `&`, `%` and `_` — see the build trap below
for what a raw `#` in a title does. Briefs pass through `latexify()`, which
turns backticks into `\code{}` and refuses a bare `^` or a brace.

### The parity checks, and why each exists

`tools/parity.py` is the single parity tool. Run it before every commit; CI
gates on it.

| Check | Catches |
|---|---|
| C1 files | A chapter in one edition and not the other |
| C3 lang catalogue | A label defined in one language only — an undefined control sequence in exactly one build |
| **C4 ordered structural signature** | A section, a listing, a figure or an exercise moved or dropped in one edition. A histogram cannot see reordering |
| C5 labels, C7 values, C9 diagrams, C11 exercises | A `\label`, a `\val{}` key, a figure key or an exercise key present in one edition only; C7 also reports a value nothing uses and a key no script produces |
| **C10 notation** | A bare decimal inside maths (the Polish edition owes a comma; write `\num{}`), a `\val{}` inside a listing, and a straight quote in Polish prose where `\enquote{}` is owed (soft) |
| **C12 numeric literals, in order, strictly** | A translated number silently changing. The Polish decimal comma is deliberately not normalised away |
| C13 verbatim ASCII | The `listings` UTF-8 trap |
| C14 macro histogram | A `\trapbox`, a `\csbox` or an `\index` dropped in translation |
| C15 main-file wiring | A main file rewritten with a chapter of front matter dropped |
| `reflist.py` | `\label{ch:asyncio}` resolving to Chapter 8 in one edition and 9 in the other |
| `check_structure.py --listings --exercises --transcripts` | A `\pyfile{}` naming a file or region that is not there; an exercise without its three files; a `\transcript{}` with no committed text |
| `check_structure.py --lines --pins --words` | The three budgets above |
| `checklog.py` | The build. **Not `grep '^!'`**: with `-file-line-error` an error line begins with a path, and `nonstopmode` writes a PDF over the top of it |

**Rules the lint cannot check, which the translator must carry** (all
inherited, all paid for in the math book): a digit stays a digit and a word
stays a word; a sentence with two maths spans, or a number and a reference,
keeps them in the same order, because C4, C8 and C12 compare in order;
listing comments stay English, because the reader is being trained to read
English code; never translate the spelling of an identifier; where an
English term has no Polish form in real use, keep the English word and
inflect it Polish — *embedding*, *token*, *batch*, *middleware* are what
Polish engineers say. **Version numbers and exercise numbers are labels,
not quantities**: `Version~0.1` in prose, never `$0.1$`, or the Polish
edition prints `0,1` and C10 is right to refuse it.

---

## Structure

Five parts, fourteen chapters, five appendices. Each chapter's brief is in
`tools/chapters.json` and prints in its stub; `notes/01-curriculum.md`
carries the reasoning, the experiments, the release plan and the overlap
rules against the companion volumes, and deliberately does not repeat the
briefs.

| Part | Chapters | Release |
|---|---|---|
| I — Runtime and toolchain | 1 CPython and the GIL · 2 Environments and packaging · 3 Typing | v0.1 |
| II — The language, mapped | 4 Objects and data · 5 Functions and control flow · 6 Errors · 7 Imports and DI | v0.1 |
| III — Concurrency | 8 asyncio for people who know `Task` | v0.2 |
| IV — Shipping | 9 Services · 10 Data · 11 Testing and trace-assert · 12 Observability and operations | v0.2 |
| V — Python for AI work | 13 The AI engineer's kit · 14 trace-assert, complete | v1.0 |
| Appendices | A Cheat sheet · B Traps · C Tool matrix · D Twenty interview problems · E Manifest (generated) | v1.0 |

**Writing a chapter means deleting the `\chapterstub{}` block and replacing
it with the chapter.** If the brief turns out to be wrong once the code has
been run, change it in the manifest and record the contradiction here under
*Resolved questions*.

**The overlap rules are the strictest thing in the manifest.** The trilogy
is one book in three volumes, so a topic has exactly one owner. Chapter 8 is
the sharpest case: the LangChain book's Chapters 3 and 4 own the event loop,
cancellation and the measurements in depth, and Chapter 8 here is the
translation view — it points there in one sentence and never repeats a
section. The full table is `notes/01-curriculum.md` §6.

**The trap catalogue** — `notes/02-traps.md` — is the source of authority
for Appendix B: every entry names the chapter that elicits it, and a trap is
put to the reader before it is named.

### The guiding project

`trace-assert`, under `code/src/trace_assert/`: a Python port of the first
layer of [agent-eval-bench](https://github.com/konradcinkusz/agent-eval-bench),
deterministic assertions over an execution trace, in pytest. The skeleton
(`Event`, `Trace`, one test) is in the tree and CI runs it; stage 01 lands
in Chapter 11, stage 02 in Chapter 13, and Chapter 14 completes, packages
and publishes it and compares the three ports.

**The assertion list is that project's own and must be copied from its
specification when Chapter 14 is written, never reconstructed from
memory.** The count printed in the book is whatever the specification says.
The repository was not consulted while scaffolding, so nothing here names
an assertion type.

---

## Build

```bash
make            # numbers, diagrams, both editions, then every gate
make en / pl    # one edition, and check its log properly
make code       # uv sync --locked, ruff, pyright, pytest with the solutions
make starters   # every exercise starter must FAIL its test
make numbers    # regenerate figures/values and figures/transcripts from code/measure
make verify     # fail if any committed number or transcript has drifted
make diagrams   # render every .mmd (needs Node; uses the sandbox's Chromium)
make check      # gen_stubs --check, parity, check_structure, checklog, reflist
make debt       # every outstanding-work ledger
make site       # assemble locally exactly what CI publishes to Pages
```

**The gates that read the source run in seconds and need no PDF. Run them
before a build, not inside it** (inherited, and paid for): `parity.py`,
`check_structure.py --all`, `gen_stubs.py --check`.

CI (`build.yml`): `code` first — lock, sync, ruff, pyright, the solutions
run, the starters run, and the measurement scripts with a drift check —
and everything gates on it; then `parity` and `diagrams`; then `build` as a
matrix over both editions on a full TeX Live; then `crossrefs` out of the
two `.aux` trees; `ledgers` and `versions` are advisory and publish to the
step summary. `pages.yml` builds both editions on every push to `main` and
publishes them with `docs/index.html`; `release.yml` attaches both PDFs to
a `v*` tag.

**The PDF has an address**, once a human has clicked once: creating a
repository's first Pages site is an administrative action no workflow token
can be granted, so `pages.yml` fails at `configure-pages` until a repository
admin sets Settings → Pages → Source to *GitHub Actions*. The workflow says
so in its own step summary when that is what failed.

### Build traps already hit and fixed

Each cost time; none is obvious from its error message. The inherited ones
are listed by name and their reasoning is in the companion books.

- **newtx without TeX Gyre dies on the copyright page.** `newtxtext` takes
  its TS1 symbols (`\textcopyright`, `\textdegree`) from TeX Gyre Termes,
  which Debian packages separately as `tex-gyre`. An `apt-get` of
  `texlive-fonts-extra` alone gives a machine with `newtxtext.sty` and
  without `ts1-qtmr.tfm`, and the run dies with `Font TS1/ntxtlf/m/n/10.95
  =ts1-qtmr ... not loadable`. **There is no inert-safe probe for a font
  metric in pdfTeX**, and both obvious ones were tried and measured before
  being rejected: `\IfFileExists{ts1-qtmr.tfm}` searches TEXINPUTS rather
  than TFMFONTS, so it reported the metric *missing on a machine that had
  it* (which would have silently switched CI to Latin Modern), and
  `\suppressfontnotfounderror` is a LuaTeX primitive that pdfTeX reports as
  an undefined control sequence. So the preamble guesses nothing: CI's full
  TeX Live is the reference, and locally the fix is `apt-get install
  tex-gyre`.
- **A raw `#` in a chapter title poisons the contents file, and the poison
  survives the fix.** `\chapter{The C# to Python cheat sheet}` fails at the
  chapter line with `Illegal parameter number in definition of
  \GetTitleStringResult`, which names neither the character nor the cause.
  `gen_stubs.py`'s `title()` now escapes it. **But the first build after
  the fix failed again**, on `main-en.toc` reading `C####`: the previous
  run had written the doubled parameter character into the `.toc`, and
  latexmk's first pass read it back before rewriting it. Clear the aux
  tree — `latexmk -C` does **not** remove the per-`\include` `.aux` files
  under `chapters/` and `appendices/`, so `make clean` does — and the next
  build is clean. The same shape as the math book's killed-latexmk NUL-file
  trap: an error naming a `.toc`, `.aux` or `.out` rather than a `.tex` is a
  stale auxiliary, not a source error.
- **A `\@starttoc` list at subsection level prints empty under
  `tocdepth=1`.** The exercise and diagram manifests write their entries
  with `\contentsline{subsection}`, and the contents depth is 1 so the
  contents stays readable — so both lists printed their heading and nothing
  under it, with no warning, on the scaffold's first clean build. The two
  list macros now raise `\c@tocdepth` inside a group around `\@starttoc`.
- **The scratchpad's `.out` file is hyperref's `.out` file.** A probe run
  as `pdflatex -output-directory=$S probe.tex > $S/probe.out` writes the
  console log into the file hyperref reads back as its bookmarks, and the
  next run typesets *This is pdf-TeX, Version...* as a bookmark string and
  reports an overfull box for it. The probe looked like a measurement and
  was not; it is the recorded instrument class — the tool accepted the
  input and returned a plausible answer. Redirect a probe's console to
  `.stdout`, never `.out`.
- **`\listxadd` on a macro that does not exist yet.** The values block did
  `\listxadd{\pyvalues}{...}` before anything had defined `\pyvalues`;
  etoolbox raises an undefined control sequence. `\newcommand{\pyvalues}{}`
  before the block.
- **uv 0.8 knows Python 3.14 only as a release candidate.** `uv python
  install 3.14` on the sandbox's preinstalled uv offered `3.14.0rc2`; uv
  0.12.13 installs 3.14.7. The Makefile takes `UV ?= uv`, so a newer binary
  on `PATH` is enough, and CI pins the uv version in `setup-uv`.
- **`siunitx` is in `texlive-science` on Debian**, not in `texlive-latex-extra`.
- **A background `make ... > log 2>&1; echo "MAKE_EXIT $?"` is reported as
  exit 0 whatever make did** (inherited). Read the log's own `MAKE_EXIT`
  line, and treat an unchanged page count as a failed build.
- **`make verify` reads uncommitted as stale and staged as current**, by
  design, because testing `git status --porcelain` would make the gate
  unusable mid-commit. So `git add figures/values figures/transcripts` is a
  step in the loop, not a way round the gate. On the scaffold's first tree
  it reported all three computed files as *never been compared to
  anything*, which is what an untracked file should say.
- **`babel` with a missing language is fatal; `fancyhdr` overwrites
  `\chaptermark` at `\pagestyle{fancy}`; `amssymb` beside `newtxmath` is a
  fatal clash invisible on a bare machine; `\IfFileExists` branches need
  `##1`** (all inherited; the preamble already handles each).

---

## Resolved questions

### The scaffold pass, September 2026

**Pinned on 14 September 2026, every one verified against PyPI on the day:**

| Package | Version | | Package | Version |
|---|---|---|---|---|
| Python | 3.14.7 | | pytest | 9.1.1 |
| uv | 0.12.13 | | pytest-asyncio | 1.4.0 |
| ruff | 0.16.7 | | hypothesis | 6.168.0 |
| pyright | 1.1.414 | | httpx | 0.28.1 |
| mypy | 2.3.1 | | structlog | 26.1.0 |
| pydantic | 2.13.5 | | opentelemetry-sdk | 1.44.0 |
| pydantic-settings | 2.15.0 | | polars | 1.44.2 |
| fastapi | 0.141.1 | | anthropic | 1.5.0 |
| uvicorn | 0.53.0 | | openai | 3.13.0 |
| sqlalchemy | 2.0.52 | | pip-audit | 2.10.1 |
| alembic | 1.20.0 | | | |

`preamble.tex` is the record and `tools/check_versions.py` is the check;
this table is a snapshot and will go stale first.

**The brief said pytest 8; the pin is 9.1.1.** The current release on the
day the pins were verified was 9.1.1, and pinning a major behind on day one
would have the reader install something the book was not run on. Every
listing that is written against pytest is written against 9.

**One-sided A4, `openany`, symmetric margins.** The book is read on a screen
beside an IDE, so mirrored margins and blank versos are a print convention
that costs the reader page turns and buys nothing. `tocdepth` is 1, because
fourteen chapters with numbered sections would make the contents longer
than a chapter.

**Appendix E is generated and was not in the brief.** The brief had four
appendices. The ledgers the math book learned to print for the reader
needed a fifth, and it is computed by `code/measure/ledgers.py` rather than
written; it is the one appendix marked *written* on the scaffold, and the
generator knows to leave it alone.

**The two diagrams were drawn and not placed.** The scaffold's first clean
build had `book-map` and `reading-loop` rendered and no `\mermaidfig` in
either edition — the ledger counted the sources and nothing counted the
placements, which is exactly the gap `check_structure --listings` closes
for listings and nothing closed for figures. Both are placed now, in the
same position in both editions, so C4 sees a move.

**A Mermaid `direction` inside a subgraph is ignored when an edge crosses
the subgraph boundary.** The reading loop was first drawn as five nodes in
one `flowchart LR` row and rendered 822 pt wide, which at `0.95\linewidth`
on this page sets the node text at under half body size. Redrawn as two
`direction LR` subgraphs stacked in a `flowchart TB`, it came out 310 by
492 pt: mermaid drops the inner direction when the loop's edges cross
between the subgraphs, so the five nodes stacked vertically and the height
cap bound instead. What worked is fewer, wordier nodes in one row, three of
them, at 524 pt in English and 555 in Polish -- the width formula the math
book records (`12.57 pt x min(400/W, 287/H)` at this geometry) predicts the
type size to a tenth of a point, and the rule that goes with it holds here
unchanged: above an aspect ratio of about 1.4 only the width matters, and
wordier nodes widen a chain. Measure `pdfinfo` before writing the caption.

**The introduction and *How to use this book* each carried a section called
*Both languages, one source*, saying nearly the same thing** -- and the
introduction's copy ended with one line alone on a page in the English
build. The introduction's section is gone and the one sentence it had that
the other lacked (the inflection rule for borrowed terms) moved into
*How to use*, in both editions, so C4 and C14 moved identically.

**`check_structure.py --pins` first matched every `\newcommand` with a
comment.** Its regex now asks for a macro whose name ends in `ver`, a body
that starts with a digit and a trailing comment that is a single
distribution name — which is what a pin line is and nothing else in the
preamble is.

**A listing line fits to 89 columns.** Measured with a sweep from 79 to 100
characters in a standalone probe using the book's own preamble: the first
overfull line is 90 characters, at 4.5 pt, and each further column costs
4.75 pt. So the 79-column rule is not the page's limit; it is ruff's, and
the ten spare columns are the slack that keeps a listing off the margin
under any metric.

**Two decisions left open, deliberately:**

- **Whether CI compiles the C# side of Appendix D.** Every Python solution
  has a test CI runs. The C# solutions are listings too, and compiling them
  needs a .NET SDK in the workflow. Decide before Appendix D is written.
- **Where the free-threaded interpreter runs for E1.** `uv python install
  3.14t` gives `python3.14t`; whether the `code` job installs two
  interpreters or E1 runs in a job of its own is undecided.

---

## After each pass

1. `python3 tools/parity.py`, `python3 tools/check_structure.py --all`,
   `python3 tools/gen_stubs.py --check` — **before** the build; they read
   the source and cost seconds
2. `make code && make starters` — every solution passes, every starter fails
3. `make numbers` and `git add figures/values figures/transcripts`, then
   `make verify` — no drift
4. `make en pl` — zero errors, zero unresolved references, zero overfull
   vboxes; `checklog.py` says so, `grep '^!'` cannot
5. `make debt` — confirm the ledgers moved the way you expected, then
   update the Status table and the ledgers at the top of this file, **from
   the build in front of you**
6. Record anything that contradicted the brief under *Resolved questions*,
   including contradictions of a note written during an earlier pass

**Note on tagging:** `git push --tags` returns HTTP 403 through the
sandbox's git proxy, so tags created in a web session exist locally only.
Tag from a local clone.

---

## What is left

Nothing in the book is written. The outstanding work is tracked as GitHub
issues under the `chapter`, `appendix`, `experiment` and `infrastructure`
labels — **work from the labels, not from a list here**, because a list in
this file is the class of claim nothing can check. In rough order:

1. **Chapters 1 to 7**, which are v0.1. Suggested order: 1, 2, 3 first,
   because every later chapter's listings assume the reader trusts the
   environment; then 4 to 7 in order, each leaning on the last.
2. **Chapters 8 to 12** (v0.2), with the trace-assert stage 01 in Chapter 11
   and experiments E4 to E7.
3. **Chapters 13 and 14 and Appendices A to D** (v1.0). Appendix B is
   written from `notes/02-traps.md`; Appendix C's version column prints
   from the preamble's macros and is never typed; Appendix D needs the
   open decision above settled first.
4. **The eight experiments**, each free, each writing a value file that a
   chapter reads with `\val{}`.
5. **The first Pages deployment**, which needs one human click.

**Do not fill a measurement table with plausible numbers.** An empty table
is load-bearing.
