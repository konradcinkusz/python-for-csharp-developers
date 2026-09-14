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
| Chapters | **3 of 14 written: Chapters 1, 3 and 7 — both editions** | 2, 4–6, 8–14 |
| Appendices | **E (Manifest), generated.** A–D are briefs | A, B, C, D |
| Code | `code/` is a locked uv project: the `trace-assert` skeleton, Chapters 1, 3 and 7's listings and exercises, the measurement scripts, and CI runs all of it | every other chapter's listings and exercises; seven of the eight experiments |

**The scaffold plus three chapters.** The scaffold existed so that the shape of
the book could be argued with before any chapter was written, and so that the
first one was written into a build that already had every gate. Chapters 1, 3
and 7 were written in parallel, by separate passes, each against the issue
that came up first rather than against the reading order — which is possible
because a chapter names what it borrows and borrows little. The gates earned
their keep on all three; see the three pass notes below.

**Two editions, one paper size, both clean.** A4 at 12pt, single-sided, the
format the book is read in — there is no print format and there will not be
one.

| | Pages | Errors | Unresolved | Overfull hbox | Overfull vbox |
|---|---|---|---|---|---|
| `main-en` | 75 | 0 | 0 | 0 | 0 |
| `main-pl` | 76 | 0 | 0 | 0 | 0 |

**Re-measure both rows from the build in front of you** after any change; a
page count carried across a layout change is the first thing in this file
to go stale. **And say which build**, which is the Chapter 3 pass's rule and
which the Chapter 1 and Chapter 7 passes then paid for independently: these
two rows are from an installation that HAS `newtx` and `inconsolata`, where
the scaffold's 37 and 37 and Chapter 3's 53 and 56 were from a bare one that
degrades to `lmodern` through the preamble's `\IfFileExists` probes.
Different fonts, different line breaks, different pagination. CI compiles on
a full TeX Live; that is the inherited two-machines rule and it is not a
defect. Record which installation you measured on, every time.

**Debt ledgers, reported by CI on every build** (`make debt`), and printed
for the reader in Appendix E, which `code/measure/ledgers.py` computes from
the tree so that `make verify` fails when a ledger moves and the appendix
does not:

- **11 of 14 chapters are stubs, in each edition; 4 of 5 appendices are**,
  and both editions agree about what is written
- 48 listing references, every file and region present · 12 exercises, each
  with a starter, a solution and a test · 24 transcript references, every
  file present · 81 code files, none over 79 columns · 19 pins agree between
  `preamble.tex` and `code/pyproject.toml`, and uv's pin agrees with three
  workflow steps
- **0 `verifybox` blocks.** Keep it that way: a box is a promise to the
  reader that something was not run
- 20 Mermaid sources, ten per language, all rendering, all placed
- 50 computed value keys, every one produced and every one used
- Parity: 23 file pairs, 0 failures, 0 warnings · 77 labels in each edition,
  0 mismatches
- Word budgets, of 3000: `ch01-runtime` at 2399 English and 2098 Polish;
  `ch03-typing` at 2915 and 2516; `ch07-imports-di` at 2581 and 2242
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

> **Network note**, extended by the Chapter 1 pass, which needed all of it.
> Reachable: `pypi.org`, `files.pythonhosted.org`, `archive.ubuntu.com`, and
> **`raw.githubusercontent.com`**. Blocked by the proxy: Ubuntu PPAs,
> `astral.sh`, `peps.python.org` and `docs.python.org`; `api.github.com`
> needs `add_repo`. Two consequences worth knowing before you start:
>
> - **uv is installed from PyPI, not from `astral.sh`.** The sandbox ships
>   uv 0.8, which knows 3.14 only as a release candidate. `python3 -m pip
>   install --target <dir> uv==0.12.13` and put its `bin/uv` on `PATH`; the
>   Makefile's `UV ?= uv` then picks it up, and `uv python install 3.14.7`
>   and `3.14.7+freethreaded` both work.
> - **A PEP number is verified from CPython's repository, not from
>   `peps.python.org`.** `Doc/whatsnew/<minor>.rst` at the tag matching the
>   pin is the primary source this sandbox can actually reach, it is the
>   authority level this list already prescribes, and it carries more than
>   the PEP number: Chapter 1's citations for PEP 703, 779 and 744, for
>   free-threaded builds not supporting the JIT, and for CPython's own
>   five-to-ten-per-cent single-thread figure all came out of one fetch of
>   `v3.14.7/Doc/whatsnew/3.14.rst`.

**Run listings, or mark them.** Every listing is a file under `code/`,
pulled in with `\pyfile{}` or `\pyregion{}`, and `code/tests/test_listings.py`
runs every `chNN/*.py` as a script on every push. Both macros print the
file's repository-relative path above the listing, because that is the path
the reader opens in the editor and the front matter promises it; `\pyregion`
prints the named `# --8<-- [start:name]` region with the file's own line
numbers, so the reader can see where in the file it sits. Anything that is not run
that way goes inside `\begin{verifybox}`. Removing a verifybox means you ran
the code — not that you reread it and it felt right. Nothing ships to a
reader with one attached.

**An exercise is three files, and the starter must fail.**
`\begin{exercise}{key}{title} … \end{exercise}` in the prose is tied to
`code/exercises/chNN/<key>.py` (the
starter the reader opens), `code/exercises/chNN/solutions/<key>.py` (what
CI runs), and `code/exercises/chNN/test_<key>.py`. `make code` runs the
solutions with `PYBOOK_SOLUTIONS=1`; `make starters` runs the starters with
`PYBOOK_STARTERS=fail`, under which `code/exercises/conftest.py` marks every
test strict-xfail — so a starter that accidentally passes is a build
failure, and so is a solution that fails. `check_structure.py --exercises`
refuses an exercise whose three files are not all there, refuses the old
`\exercise{key}{title}{body}` macro form outright, and an exercise key must
carry its chapter's number (`e07_02_...` in Chapter 7, `e00_...` in the front
matter). It is an environment and not a macro because a macro argument
cannot hold verbatim material: the first exercise whose body showed a
`\begin{python}` fragment would have died inside the braces. That triple is what makes *PDF on the left,
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
fails when the two disagree, compares `\pypatch` with
`code/.python-version`, and compares `\uvver` with the `version:` of every
`setup-uv` step in `.github/workflows/` — uv is not in `pyproject.toml`, it
installs `pyproject.toml`, so its pin lived in four places by hand and
nothing compared them. Never write a version number into a chapter; a
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
| **C10 notation** | A bare decimal inside maths (the Polish edition owes a comma; write `\num{}`), a `\val{}` inside a listing, and a straight quote in Polish prose where `\enquote{}` is owed (soft) — prose only: a quote inside `\code{}` is what the reader types |
| **C12 numeric literals, in order, strictly** | A translated number silently changing. The Polish decimal comma is deliberately not normalised away |
| C13 verbatim ASCII | The `listings` UTF-8 trap |
| C14 macro histogram | A `\trapbox`, a `\csbox` or an `\index` dropped in translation |
| C15 main-file wiring | A main file rewritten with a chapter of front matter dropped, and (after the second review round) a front-matter file's `\input` line deleted from the shared `body.tex` itself, which drops it from both editions identically |
| `reflist.py` | `\label{ch:asyncio}` resolving to Chapter 8 in one edition and 9 in the other |
| `check_structure.py --listings --exercises --transcripts` | A `\pyfile{}` naming a file or region that is not there; an exercise without its three files; a `\transcript{}` with no committed text |
| `check_structure.py --lines --pins --words` | The three budgets above, and uv's pin across the workflows |
| `checklog.py` | The build. **Not `grep '^!'`**: with `-file-line-error` an error line begins with a path, and `nonstopmode` writes a PDF over the top of it. Also hard on `Font shape … undefined` and hyperref's `Token not allowed`, both of which it used to ignore and both of which hid a shipped defect |

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
`check_structure.py --all`, `gen_stubs.py --check`. `make check` fails on
a parity failure; it did not until the review pass, because the recipe
piped `parity.py` into `tail` and make saw tail's exit status.

CI (`build.yml`): `code`, `parity` and `diagrams` run side by side — `code`
locks, syncs, runs ruff, pyright, the solutions, the starters and the
measurement scripts with a drift check — and `build`, the compile matrix
over both editions on a full TeX Live, `needs` all three, so a red parity
check blocks the compile; then `crossrefs` out of the two `.aux` trees;
`ledgers` and `versions` are advisory and publish to the step summary.
`pages.yml` builds both editions on every push to `main` and publishes them
with `docs/index.html`; `release.yml` attaches both PDFs to a `v*` tag.
Both run the same source gates first, and `release.yml` runs pyright and
the starters exactly as the `code` job does, because a push straight to
`main` and a tag are not checked by `build.yml` before they publish.

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
- **`binhex.tex` is in `texlive-plain-generic`**, and `newtxmath` needs it.
  With the font packages installed but not that one the run dies on
  `! LaTeX Error: File 'binhex.tex' not found.` after the preamble has
  already loaded newtx, so the message names a file nobody wrote and no
  package this book asks for. The full local set is `latexmk`,
  `texlive-latex-base`, `-latex-recommended`, `-latex-extra`,
  `-fonts-recommended`, `-fonts-extra`, `-science`, `-lang-polish`,
  `-lang-english`, `-plain-generic` and `tex-gyre`.
- **A `\pyvaltext` body reaches the page as LaTeX, so the script that
  writes one owes it the same escaping a chapter owes.** `platform.machine()`
  on the commonest architecture in the world returns `x86_64`, the
  underscore is a maths subscript, and Chapter 1's first build died on four
  `Missing $ inserted` errors and two overfull boxes of 98.8 and 74.7 pt — the second of which is a paragraph typeset in maths mode with its
  spaces gone, which is what an unclosed `$` does. `code/measure/e01_gil.py`
  carries a `tex()` helper; any script emitting a text value needs one.
  `\pyval` needs none of it, because a number has no special characters in
  it.
- **A background `make ... > log 2>&1; echo "MAKE_EXIT $?"` is reported as
  exit 0 whatever make did** (inherited). Read the log's own `MAKE_EXIT`
  line, and treat an unchanged page count as a failed build.
- **And the scaffold's own first CI run failed on exactly that trap.** The
  code workspace's checks were run once as a background job whose compound
  command ended in an `echo`, the notification said exit 0, and the log was
  never read for the exit lines of the steps inside it. pyright had failed
  on two errors the whole time — a private-name use in the first listing and a
  `default_factory=dict` that a strict checker types as
  `dict[Unknown, Unknown]` — and CI found both in forty seconds. **Run
  `make code` in the foreground before a push, and read pyright's own last
  line.** The `dict[Unknown, Unknown]` half is worth keeping as Chapter 3
  material: it is the checker being right about a default that is
  untyped, and the fix is a named factory with a return type.
- **`make verify` reads uncommitted as stale and staged as current**, by
  design, because testing `git status --porcelain` would make the gate
  unusable mid-commit. So `git add figures/values figures/transcripts` is a
  step in the loop, not a way round the gate. On the scaffold's first tree
  it reported all three computed files as *never been compared to
  anything*, which is what an untracked file should say.
- **A make recipe that pipes a gate into `tail` cannot fail.** A pipeline's
  exit status is its last command's, and `/bin/sh` has no `pipefail`, so
  `python3 tools/parity.py | tail -n 3` reported parity's summary and could
  never fail `make check` however many checks were red. Proved by adding a
  one-edition `\label` and running `make translate`: exit 0 before the fix,
  `Error 1` after. The recipe now captures the output and tests the
  command's own status.
- **listings' `linerange` does not take marker strings as its two ends.**
  The inherited `\pyregion` wrote `linerange={--8<--\ [start:x]--- 8<--\ [end:x]}`,
  which matches nothing, and listings then printed the **whole file** with
  no warning — measured on a three-region probe file. The working form is
  `rangebeginprefix`/`rangeendprefix` (and the two suffixes) set once, with
  `linerange={name-name}`; it matches an indented marker too. The same
  definition sits in llm-book's preamble, unused there.
- **hyperref keeps the argument of a `\color` it removes from a bookmark.**
  A section title with `\api{model\_validate}` made a bookmark reading
  `mtealmodel_validate` and two `Token not allowed` warnings — which
  `checklog.py` ignored by name. `\def\color#1{}` inside
  `\pdfstringdefDisableCommands` gobbles the colour name, and the warning is
  hard now.
- **inconsolata has no italic.** `commentstyle=\itshape` produced
  ``Font shape `T1/zi4/m/it' undefined`` on every build, substituted with
  upright, and `Font shape` was in `checklog.py`'s ignore list. The comment
  style is colour only, and the warning is hard now.
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

**Two decisions left open, deliberately** — one of which the Chapter 1
pass has since settled:

- **Whether CI compiles the C# side of Appendix D.** Every Python solution
  has a test CI runs. The C# solutions are listings too, and compiling them
  needs a .NET SDK in the workflow. Decide before Appendix D is written.
- **Where the free-threaded interpreter runs for E1.** `uv python install
  3.14t` gives `python3.14t`; whether the `code` job installs two
  interpreters or E1 runs in a job of its own is undecided.
  **Settled in the Chapter 1 pass: neither, and CI installs one
  interpreter** — a timing is recorded once into a committed JSON and CI
  only re-derives the value file from it, so nothing in CI ever needs the
  free-threaded build. See that pass below.

### The review pass, September 2026

An adversarial review workflow — seven finder lenses, three refuters per
finding — was run over the scaffold before chapter 1. Its first run died on
a session limit with only the LaTeX and CI lenses finished, leaving
seventeen unverified candidates; the second run resumed those two from
cache. **The seventeen were verified by hand while the second run was in
flight, and fourteen held**, every one settled by opening the file or by a
probe against this preamble rather than by reading the candidate:

- `make check` and `make translate` could not fail on parity (above).
- `build` did not `needs: parity`, so a PR could carry a green compile beside
  a red parity job, whatever the "hard gate" comment said.
- `pages.yml` and `release.yml` ran no source gate, and `release.yml` ran
  neither pyright nor the starters.
- uv's version sat in `preamble.tex` and three workflow steps by hand.
- `code/README.md` and the pyproject header said `uv run pytest` runs the
  solutions; it runs the starters and is red on a pristine checkout by
  design. `PYBOOK_SOLUTIONS=1` is what CI runs.
- Appendix E printed *1 listing files* and *1 exercises*, in both languages
  (Polish has three plural forms to get wrong). The counts are a table now,
  and the page says why.
- *How to use this book* said a listing's path is printed above it, and
  `\pyfile` printed only a caption below. Fixed in the direction the
  reader needs: the macro prints the path.
- `\pyregion` printed the whole file (above).
- An exercise body could not hold a listing (above; now an environment).
- `\api{}` in a title leaked its colour name into the bookmark (above).
- `\itshape` comments on a font with no italic (above).
- Both language files' comment on `\dash` said the English dash is closed
  up; every use is spaced, as the math book's contract says.
- `gen_stubs.py`'s `latexify()` ran its `\enquote{}` rewrite over the whole
  brief after the `\code{}` conversion, so chapter 1's stub printed curly
  quotes inside `if __name__ == "__main__"`. The rewrite runs over prose
  segments only, and C10's straight-quote rule is scoped the same way.
- `\lblMeasured` had no consumer and `\lblValueMissing` had none either;
  the first is gone and the second is what `\val{}` prints for a missing key.

Three were not taken: the 88-versus-89-column off-by-one, because no file
says 88; the claim that microtype expansion changes the column measurement
between this machine and CI, because it was not established either way and
expansion does not act inside a listing's `\hbox`; and `\code{}`
hard-coding `\small`, which is true and harmless until a `\code{}` lands in
a `\footnotesize` context — recorded here so that whoever meets it knows it
was seen.

**What the pass earned.** A CI comment claiming a gate is one more claim
about the tree: "parity is a hard gate" was written into `build.yml` above a
job graph in which parity gated nothing. And an ignore list in a log checker
is where a defect goes to become permanent: two of the fourteen were sitting
in `main-en.log` on every build, under strings `checklog.py` had been told
to skip.

**A second round, from the `find:code` and `find:gates` lenses**, which had
not finished in the first pass and completed once resumed. Eight more held,
every one reproduced on a scratch copy before being fixed:

- **Blocker, the sharpest of the whole review.** `written()` — in
  `gen_stubs.py`, `check_structure.py` and `ledgers.py` — tested a chapter
  file for the raw substring `\chapterstub{`, and the header the generator
  itself writes NAMES that macro in a sentence of prose. So a chapter
  written exactly as instructed (delete the block, keep the header, write
  the chapter) stayed classified as a stub forever: `gen_stubs.py --check`
  went red on the first written chapter, and a bare `gen_stubs.py` run
  silently overwrote the written prose with a fresh stub, with no warning
  of any kind. Reproduced by faking 700 words of "written" chapter 1 with
  the header intact: before the fix, `gen_stubs.py` deleted it; after, it
  left it alone and correctly regenerated the other thirteen (genuinely
  unwritten) stubs, whose header wording had also changed. All three
  `written()`/`count_stubs()` functions now strip comments before testing,
  and the header no longer needs the literal token to make its point.
- **`code/tests/test_listings.py` failed a listing that exits 0 via
  `sys.exit(main())`** — the ordinary idiom for a script with a return
  code. `runpy.run_path` in-process lets that `SystemExit(0)` propagate
  into pytest, which reports it as a FAILURE. Reproduced on a throwaway
  `ch01/exits.py`. Fixed by running each listing as a real subprocess,
  which is also a closer match to what the front matter tells the reader
  to do (`uv run python chNN/file.py`, from `code/`) than an in-process
  `runpy` call ever was.
- **`code/pyproject.toml`'s pyright `include` hard-coded `ch00`**, so no
  chapter written after the first would ever be strictly type-checked
  while the CI step stayed green. `include = [..., "ch*", ...]` — pyright's
  glob syntax — matches every chapter as it arrives; proved by adding a
  scratch `ch01/probe.py` and watching the analysed-file count move.
- **`PYBOOK_SOLUTIONS` was read with a bare truthiness test**, so
  `PYBOOK_SOLUTIONS=0` — an explicitly-off value — loaded the solutions
  anyway, because `"0"` is a non-empty string. Now compared against
  `("0", "")` for off; proved with `PYBOOK_SOLUTIONS=0`, unset and `=1`,
  all three giving the intended answer.
- **The transcript ASCII guard let an ANSI escape or a raw tab through**:
  `ord(ch) > 127` catches multi-byte characters and nothing under 128,
  which includes ESC (a colour code a library might emit) and tab.
  `listings` prints an escape sequence as visible mojibake, or expands a
  tab past the 79-column budget the guard has already cleared it against.
  Now also rejects any character under 32; reproduced with `\x1b[31m`
  and a literal tab before the fix, caught after it.
- **`ledgers.py`'s `count_re` (verifybox, exercise counts) was not
  comment-stripped**, where `check_structure.py`'s equivalent checks
  already are — so a `% \begin{exercise}{...}` commented out while
  drafting was counted by Appendix E and `make debt` and by nothing else.
  Reproduced by commenting one out and watching the two tools agree at 1
  either way after the fix.
- **A listing file in a chapter's own subdirectory was never run and
  never counted.** `test_listings.py` and `ledgers.py` both globbed
  `chNN/*.py` non-recursively, while `\pyfile{}` can point at any path
  under `code/`. Both now use `rglob`, so a nested file is run and counted
  the same way it can be printed.
- **C15's front-matter check tested only that FOUR MACRO CATEGORIES exist
  in `body.tex`**, not that any particular file is `\input` there — so
  the defect this check exists for (a sibling repository once shipped a
  main file with the introduction dropped) is possible again now that the
  two main files share one `body.tex`: deleting one `\input` line drops
  the same file from both editions at once, and the four categories are
  still each present from something else. Reproduced by deleting
  `\input{frontmatter/\booklang/introduction}` from `body.tex`: every
  other gate stayed green and C15 said nothing, before the fix. It now
  requires every file physically present under `frontmatter/en/` to be
  `\input` somewhere in `body.tex`, and the deletion above is now caught
  by name.
- **A bare `$` in a brief — inside `` \code{} `` or in plain prose —
  opened LaTeX maths mode and swallowed the rest of the paragraph**
  (`Missing $ inserted`, reproduced on a standalone probe with
  `` `$HOME` `` in a brief). `$` is escaped in both branches of
  `latexify()` now, the same way `&`, `%`, `#` and `_` already are.

Both editions still build to 37 pages with zero errors, zero unresolved
references and zero overfull boxes; parity reports 0 failures and 0
warnings; `reflist.py` 27 labels in each edition, 0 mismatches; every code
gate green, including the rewritten `test_listings.py`.

**Four candidates from the second round were considered and not taken**,
for reasons worth keeping rather than silently dropping:

- *Appendix D's twenty interview problems have no directory the exercise
  or listing mechanism can address.* True, and it is one half of the open
  decision already recorded above ("whether CI compiles the C# side of
  Appendix D") — settling the directory shape belongs with that decision,
  before Appendix D is written, not as a side effect of a review pass.
- *No source gate checks that an external `\pyfile`-referenced listing is
  ASCII; the defect is caught only by a full compile.* Real, and it is the
  same class parity's C13 already closes for in-source listing
  environments — worth a `--listings`-adjacent check one day, but every
  currently existing listing is ASCII and the full compile does catch it,
  so nothing ships wrong in the meantime.
- *In-source listing bodies are digested by C4/C12 after `%`-comment
  stripping, so an edit made after a `%` in one edition only is
  invisible.* Reconsidered rather than fixed: a comment is not page
  content, and digesting comments would make the ordered signature and
  the numeric-literal check fail on a code comment that legitimately
  differs between editions (comments stay English by rule, so a Polish
  file's comment is never even a translation of the English one) — the
  behaviour is intentional, not a gap.
- *A pin macro added to both `preamble.tex` and `pyproject.toml` is
  invisible to `check_versions.py` unless also added to its `PINS` dict.*
  True and accepted by design: `check_versions.py` maps a macro name to a
  PyPI *distribution* name, which cannot be derived from the macro name in
  general (`\pysettingsver` names `pydantic-settings`, not
  `pysettings`), so the dict is the one place that mapping can live.

### The Chapter 3 pass, September 2026

The first chapter written into the scaffold, and the gates caught five things
on the way. Every claim below was measured on the pinned versions rather than
recalled, and the scripts that measured them are in the tree.

**The brief asked why the book pins two checkers; the answer is now a
number rather than a sentence.** `code/ch03/where_it_lies.py` holds four
functions, each declaring `-> int` and each returning a `str` at run time:
two where `Any` arrives from `json.loads` and nobody decided anything, and
two where the author told the checker to stop looking (`cast`,
`type: ignore`). Measured by `code/measure/checkers.py`, which runs both
tools over that file and writes what each said:

| | pyright 1.1.414, strict | mypy 2.3.1, `--strict` |
|---|---|---|
| errors on four wrong functions | **0** | **2**, both `no-any-return` |

Neither tool is at fault. pyright is applying the type system, in which `Any`
is compatible with everything; mypy's strict profile adds an opinion the type
system does not have. **The instrument was watched producing a known answer
before the zero was believed**, which is the inherited rule and it mattered
here: a zero from a checker is exactly what a mis-configured checker also
prints. A two-line file with an untyped parameter drew four strict-only
diagnostics (`reportUnknownParameterType`, `reportMissingParameterType`),
which is how the strict mode was proved to be in effect.

A second measurement, on `code/ch03/defaults.py` — one mutable default
argument, correctly annotated — went **pyright 0, mypy 0, ruff 1** (`B006`).
So the chapter can say, with evidence, that a type checker answers questions
about types and that a good deal of what goes wrong in Python is not one.
ruff is run there with `--ignore-noqa`, because the listing carries a `noqa`
so that `make code` stays green; without the flag the script would have
measured the comment rather than the code.

**`check_structure.py --lines` caught a line `ruff check` let through, and
the disagreement is by design in ruff.** An 88-column line whose overlong
part is a trailing `# pyright: ignore[...]` pragma passes ruff's `E501` and
fails the book's own gate. Reproduced both ways on a two-line probe: a plain
86-column line is flagged, an 89-column line ending in a pragma is not. So
**ruff alone does not hold this book to 79 columns**; `--lines` is what
enforces the page width, and it is not redundant with the linter.

**`TypeIs` requires consistency, and `list` is invariant — which rewrote an
exercise.** The obvious signature for a list predicate,
`list[object] -> TypeIs[list[str]]`, is *rejected*: pyright says the narrowed
type is "not consistent with" the parameter type, because `list[str]` is not
assignable to `list[object]`. `TypeGuard[list[str]]` over the same parameter
is accepted, since `TypeGuard` has no such requirement — which is the same
fact as `TypeGuard` narrowing only the positive branch, seen from the other
side. Exercise 3.1 takes a `Sequence` for that reason, `Sequence` being
covariant, and §3.2 now carries the finding because it ties the chapter's
variance material to its narrowing material.

**Writing the chapter's own measurement script ran straight into the
chapter's own §3.5.** `isinstance(value, dict)` narrows to
`dict[Unknown, Unknown]` under strict pyright, so parsing pyright's JSON
output drew thirteen `reportUnknown*` errors. The fix is one documented
`cast` in one helper — which is one of the four holes the chapter lists,
used deliberately and in one place. That is the same complaint the scaffold
met on `default_factory=dict`, and the chapter's `projectbox` now points at
both instances.

**`make starters` caught two exercises whose tests passed on the unfinished
starter**, and both were real. Exercise 3.1's starter carried the `TypeIs`
annotation the exercise exists to teach, so the test checking for it passed
before the reader had done anything; the starter now carries `-> bool` and
the annotation is half the work. Exercise 3.3's second test called through
the shared default only once, and **one call through a mutable default is not
enough to show that it is shared** — the test now calls twice. `conftest.py`
marks *every* collected test strict-xfail, so an exercise whose starter fails
only some of its tests is a build failure, and that is the gate working.

**Two decisions, both recorded rather than taken quietly.** There is no .NET
SDK in this sandbox, so nothing in the chapter compiles C#: every C# claim it
makes is a language-level fact a reader can check in their own IDE, it uses
no `csharp` listing environment at all, and the C# side lives in two `csbox`
blocks of prose. And the exercise keys were renumbered once during the pass
so that the printed numbers follow the sections — the counter numbers
exercises by order of appearance, so `e03_01_` must be the one that appears
first, and a key whose number disagrees with its position is confusing on the
page and invisible to every gate.

**Two unmeasured comparatives got into the prose and were caught on a
re-read rather than by a gate.** Neither was a headline claim; both were
connective tissue — *pydantic is the only one that costs anything to
construct*, and *pyright is fast, mypy is slower*. The first is now a
statement about behaviour (it is the only one that does anything beyond
assigning the fields), which is checkable by reading. The second split: *the
older of the two* is verified from PyPI release metadata (mypy's earliest
release is 2009, pyright's 2021), and the speed half is **gone**, replaced by
a sentence saying the book has not measured it and neither has whoever told
you otherwise. The class is worth naming because a gate cannot see it: a
comparative that arrives as a subordinate clause reads like prose rather than
like a claim, and `grep -nE 'faster|slower|cheaper'` over a finished chapter
is the cheapest audit in this repository.

**Nothing in the brief turned out to be wrong.** All five of the trap
catalogue's Chapter 3 entries are delivered and marked in `notes/02-traps.md`
with the section that elicits each; the brief names four of them in its
*traps* clause and the fifth, `Any` propagation, in its body.

**The figures, measured with `pdfinfo` before the captions were written**,
using the inherited formula `12.57 pt x min(400/W, 287/H)`:

| | W x H (en) | W x H (pl) | binds | en | pl |
|---|---|---|---|---|---|
| `ch03-two-compilers` | 522 x 216 | 538 x 250 | width | 9.63 pt | 9.34 pt |
| `ch03-boundary` | 708 x 110 | 750 x 110 | width | 7.10 pt | 6.70 pt |

Both are above the aspect-ratio crossover, so only the width matters, and
trimming the Polish `boundary` nodes took two attempts because **the node I
trimmed first was not the widest one** — mermaid sizes a chain by the sum of
its nodes' longest lines, so the render has to be measured again rather than
reasoned about.

### The Chapter 1 pass, September 2026

**Chapter 1 is written in both editions, experiment E1 has run, and the four
Part I traps it owns are marked delivered in `notes/02-traps.md` with the
section that carries each.** Three listings under `code/ch01/`, three
exercises, three figures per edition, two transcripts. What is worth reading
below is not the chapter but what the gates refused: every defect they caught
was in work that already looked finished, and each is listed rather than
counted, because a tally here is the class of claim this file forbids.

#### A TIMING cannot pass the drift gate, so E1 has two modes

Every other script under `measure/` is deterministic: it counts the tree, or
it runs a listing whose output is fixed. A wall time is not, and CI re-runs
every script there on every push and fails the build when a committed value
moves. A timing script that measured on each run could therefore never be
green on two machines — and a wall time rounded until it could would
say nothing.

So `code/measure/e01_gil.py --record` measures and writes
`code/measure/data/e01.json`, committed, with the machine and both
interpreters recorded beside the numbers; the default mode derives
`figures/values/e01.tex` from that file and is what `make numbers` runs. The
gate then asks a question it can answer — does the page agree with the
measurement that was taken? — and re-recording is a deliberate act that
reviews as a diff of the data rather than of the prose. **This is the shape
every later timing experiment needs**, and `notes/01-curriculum.md` §4 says
so where the next person will look.

It also settles the second of the scaffold's two open decisions. **CI installs
one interpreter.** Only `--record` needs `python3.14t`, and nothing in CI
records; proved by hiding the binary from `PATH` and watching the emit mode
exit 0 and `--record` exit 1 with the install command in its message. A
second interpreter in CI would buy a re-measurement on a shared runner, which
is the one machine whose timings nobody should trust.

#### Three guards fired, each written for a defect that had not yet happened

- **The reproduce-from-the-page guard, on its first real run.** The page
  would have carried 0.097, 0.398 and 4.09, and the first two divide to 4.10.
  This is the defect both sibling books record paying for repeatedly, caught
  here by three lines of code before it reached a page. The ratios print to
  one decimal now.
- **A ratio under 1.0.** At a tenth of the present workload size the
  free-threaded four-thread run came out FASTER than the one-thread run, and
  would have printed `0.9` — four threads beating one at the same work
  each, which is not a finding but a measurement smaller than the machine's
  own noise. `emit()` now refuses a sub-unity ratio and says to raise the
  workload; `ch01/workloads.py` is sized so one unit takes about a fifth of a
  second, with few trials, and the harness repeats the whole file instead so
  a reader's own run stays about five seconds.
- **`PYBOOK_STARTERS=fail` refused an exercise test of mine.** Exercise 1.3's
  first draft had a test asserting that importing the module runs nothing —
  which is true of the untouched starter, so it passed, and a strict
  xfail reports a pass as a failure. That is the mechanism working exactly as
  designed: **every test in an exercise's file must exercise the thing the
  reader has not written yet.** A precondition belongs inside a test that
  goes on to fail, not beside it. Folded into the test that then calls
  `main()`.

#### What E1 measured, and the one number it refuses to conclude anything from

Four threads, three workloads, two builds, seven repeats of the whole
listing, on four cores. Pure-Python work takes **4.1x** as long on four
threads as on one under the default build and **1.0x** under
`python3.14t`; a socket read and a `hashlib` digest are **1.0x** on both,
because neither holds the lock. The wall-clock gain on the one workload the
lock touches is **3.8x**.

**The number everyone asks for is the one this experiment cannot give.** What
does free-threading cost a single thread? Across recordings on this machine
the two one-thread columns have differed by one, seven and eleven per cent,
against a run-to-run spread of twelve per cent in the ratios themselves. The
value is emitted — as a *difference*, computed so a reader dividing the
two printed columns gets the same answer — and the chapter quotes
CPython's own five-to-ten-per-cent estimate beside it and says plainly that
the agreement is worth nothing, because a seven-per-cent difference inside a
twelve-per-cent spread is not a measurement. An earlier recording at a tenth
of this workload said eleven per cent, which is the same non-answer wearing a
confident face.

#### The brief was right about the mathematics and wrong about one listing

**`python -m dis` cannot be a committed transcript.** Its output carries a
code object's memory address — `<code object total_due at 0x7f09...>` —
which changes on every run, so `make verify` could never be green on it,
and it disassembles the module-level code as well, which is noise around
the four lines the section is about. `dis.dis` on a function object prints
neither. The listing is `dis.dis(total_due)`; the brief in
`tools/chapters.json` now says so and says why, which is the one amendment
this pass made to it.

Two other things the brief called for turned out to be verifiable in a
stronger form than it asked:

- It says *a thread pool on CPU-bound and on I/O-bound work*. The
  chapter times **three** workloads, because the third is the one nobody
  predicts: `hashlib` over a large buffer releases the lock and scales like
  I/O. Two rows say *threads are fine* for two different reasons, and
  the brief's own payoff — which of four workloads the lock hurts
  — is the three plus the same CPU row on the free-threaded build.
- Its PEP numbers are right. They were verified out of CPython's own
  `Doc/whatsnew/3.14.rst` at tag `v3.14.7`, which was the only primary source
  this sandbox could reach, and the same fetch supplied three more things the
  chapter now cites: that free-threaded builds do not support JIT compilation
  (which the measurement had already shown, `sys._jit.is_available()` being
  `False` under `python3.14t`), that the JIT is PEP 744 and not recommended
  for production, and the five-to-ten-per-cent figure above.

#### Also

- **A starter cannot carry an import its unwritten code would use.** Exercise
  1.3's starter imported `sys` for the `sys.exit` the reader has to write,
  and ruff called it F401 on an otherwise untouched file. The import is gone
  and the trailing comment says it is missing on purpose, which is a better
  instruction anyway.
- **pyright strict rejects JSON.** Every value read back out of
  `json.loads` is `Unknown` to it, and the measurement script traffics in
  nothing else. Four `TypedDict`s and one `cast` at the boundary fixed it,
  and the driver was changed to emit a mapping of name to `[one, many]`
  rather than the listing's own mixed tuples, because a list of mixed types
  is a list of `Unknown`. This is the `dict[Unknown, Unknown]` class the
  scaffold's own pass flagged as Chapter 3 material, met for real.
- **The diagram manifest column overflows at about 70 visible characters**
  on this layout — key plus `.mmd` plus ` --- ` plus the third
  argument. Measured: 67 fits and 70 does not. That is the sibling books'
  recurring defect with a local number attached; the six entries here are 42
  to 59, and the rule is the one they record — the third argument is
  manifest copy, not a caption.
- **The figures were measured before the captions were written**, which is
  the recorded rule. All six renders land between 9.08 and 10.28 pt of node
  text against the formula `12.57 x min(400/W, 287/H)`, with every aspect
  ratio above the 1.4 crossover. The first draft of `ch01-compile-step` was
  four nodes per row at 801 pt and 6.28 pt of type; three nodes per row
  brought it to 514 pt.
- **`\pyregion` and its markers work as the preamble documents them**, on
  six regions across three files, printing the file's own line numbers.
- Chapter 1 is the first file in the book to use `\index`. The entries are
  Polish in the Polish edition, which parity allows: C14 counts `\index`
  and compares nothing inside it.
- **The page counts in the Status table above changed provenance under
  this pass**, and the Chapter 7 pass reached the same conclusion from its
  own container independently. The Chapter 3 pass measured on a bare TeX
  Live and said so, correctly, in the sentence it added; this pass installed
  the full font set to get past `binhex.tex` (the trap above), and Chapter 7
  installed it too. So the rows in the Status table are a *full*
  installation's and are not comparable with either the scaffold's 37 and 37
  or Chapter 3's own 53 and 56. Nothing is wrong with any of the three
  measurements and the rule that separates them was already written down.
  **Three sessions measuring one book on two kinds of installation is now
  something that has happened here rather than an inherited caution** — so a
  page count in this file needs its installation named beside it, and that
  row is the first thing a later pass should re-measure rather than trust.
  The merged rows also differ from each other for the first time, 75 against
  76, which is only the recorded asymmetry — Polish prose is longer and sets
  in more lines — arriving now that there is enough prose for it to show.
- **An exercise key's number must match its order of appearance**, because
  the box prints both: the first draft had `\begin{exercise}{e01_02_...}`
  third in the chapter, so the page read *Exercise 1.3* over a starter
  called `e01_02_which_pool.py`. The counter is positional and the key is
  not. `check_structure.py --exercises` checks an exercise key's *chapter*
  prefix and not its sequence, so nothing caught this; the three files were
  renamed by hand. **The check is one loop away and is deliberately not
  written here** — `tools/` is shared with whatever other chapter is being
  written at the same time, and a gate is worth its own change rather than
  a side effect of this one.

---

### Chapter 7 pass, September 2026

The first chapter written, and the brief held everywhere it made a claim
about *what the chapter should contain*. What it got wrong was the framing
every book gets wrong, and a probe settled it in a minute.

**A circular import is not an error, and the brief's “three ways out” are
three ways of moving a name lookup past import time.** Two modules that
`import` each other run fine: the module OBJECT is put in `sys.modules`
before its body runs, which is what stops the recursion, so binding it
always succeeds. What fails is a NAME read from a module whose body has not
reached the line that binds it — which is exactly what `from x import y`
asks for, at import time. So the three fixes are: hold the module rather
than the name, import inside the function, and extract the shared thing
into a third module; and only the third removes the cycle. All four cases
are in `code/ch07/cycles.py`, which runs them and prints what came out.

**THE FINDING: CPython’s diagnosis of a circular import depends on where the
file sits, not on what went wrong.** The same two-module cycle produces two
different messages:

| Where the modules are | What CPython says |
|---|---|
| inside a package | `cannot import name 'X' from partially initialized module 'p.m' (most likely due to a circular import)` |
| flat, in the directory you ran from | `cannot import name 'X' from 'm' (consider renaming 'm.py' if it has the same name as a library you intended to import)` |

Hypothesised from the first probe disagreeing with the second, then
**confirmed by moving the identical pair off `sys.path[0]` with
`PYTHONPATH`**, at which point the flat pair produced the package message.
CPython prefers the shadowing hint when the module’s file is in
`sys.path[0]`, so the message that names the cause fires in the packaged
layout and the message about a name clash fires in the flat one — which is
the shape a first Python project takes. `§7.3` carries it as a warning box,
and both halves are in the chapter’s transcript because the listing runs
both.

**The DI-library question the brief asked to settle on the day, settled.**
Read off PyPI on 14 September 2026 rather than remembered:
`dependency-injector` 4.49.1 (2026-06-18), `injector` 0.24.0 (2026-01-09),
`punq` 0.9.0 (2026-09-08), `svcs` 26.2.0 (2026-08-24), `wireup` 2.12.0
(2026-07-09) and `kink` 0.9.0 (2026-03-19) are all maintained; `lagom`
2.7.7 is over a year old and stops at 3.13. **The finding is that none of
them is the default**, which is the difference from .NET worth printing,
and the chapter says that rather than naming a winner. No version numbers
reached the page: a dated ecosystem claim is durable, a version number in
prose is not, and `\pinnedon{}` already carries the date.

**Chapter 7 added no dependency to `code/pyproject.toml`**, deliberately.
Every listing in it runs on the standard library, so the composition root is
demonstrated with `functools.partial` and `typing.Protocol` and nothing is
installed to make a point about containers.

**A listing that is MEANT to fail cannot satisfy `test_listings.py`, and the
underscore is the mechanism.** That runner executes every `chNN/**/*.py`
whose name does not begin with `_`, and half of a cycle run on its own
proves nothing. So the eight modules under `code/ch07/cycle/` and the two
`code/ch07/_flat_*.py` are underscored — which is also the ordinary Python
mark for *internal to this package* — and `code/ch07/cycles.py`, which IS
run, imports every one of them. The convention is recorded here because the
next chapter that needs a deliberately-broken module should not re-derive
it: **an underscored module is still exercised, by the driver that is not
underscored, and the driver’s docstring says so.**

**pyright strict shaped three listings, and each error was right.**
`build()` is annotated as returning a plain callable, so `build().func` is
refused — which is the composition root’s whole point, enforced rather
than asserted, and the chapter says so. An `__init__.py` with
`__all__ = ["discount"]` and no import of `discount` is
`reportUnsupportedDunderAll`, and the fix is the empty package body the
chapter argues for anyway. A constant assigned in both branches of a
`try`/`except` is `reportConstantRedefinition`; assigning it once from a
helper reads better regardless.

**Two claims written from background knowledge rather than from a probe,
both caught on a last read of the chapter and both wrong.** The C# box said
Python “makes no thread-safety promise” about a module body. It does:
`importlib._bootstrap._ModuleLock` is a lock per module, taken while a body
runs, and it detects its own deadlocks — read out of the installed
interpreter. So the box now says what is actually different, which is better
material: not thread safety, but that a cycle lets a second module see this
one half-built, which hands forward to §7.3. And the `-m` box said that
invoking a .NET DLL directly “gives you whatever the directory happens to
contain”, which is false — resolution is declared, by the project and by the
deps file beside it. The corrected contrast is sharper than the wrong one:
in .NET the directory you are standing in does not change which code loads,
and in Python it does, because `sys.path[0]` is chosen by how you started the
process. **A .NET claim in this book is the one a reader is most likely to
know better than the author**, and neither of these would have been caught by
any gate.

**Two overfull hboxes, both the inherited long-`\api{}`-at-a-line-break
class, and this book’s first.** 3.1 pt in English on
`\api{importlib.import\_module}` and 7.3 pt in Polish on
`\api{sys.modules}`. Neither hyphenates. The English one was cleared by
starting a new paragraph with the token, which puts it at the left margin
deterministically; the Polish one by moving the token earlier in its
sentence. **Both editions were rebuilt after each fix**, because a reflow in
one says nothing about the other.

**The container had no TeX at all.** `latexmk` and TeX Live are not
preinstalled in this sandbox, and `make en` fails with
`make: latexmk: No such file or directory`. What this pass installed, and
what was enough for a clean build of both editions:
`latexmk texlive-latex-recommended texlive-latex-extra
texlive-fonts-recommended texlive-fonts-extra texlive-science
texlive-lang-polish texlive-lang-english tex-gyre texlive-plain-generic`.
`tex-gyre` is on that list because of the trap already recorded above, and
`texlive-fonts-extra` brings newtx and inconsolata — so the local build
after it measures the same fonts CI does, which is why the two hbox figures
above are worth trusting.

**Three diagrams, measured before the captions were written**, as the rule
says. The first drafts came out 775 and 797 pt wide and set their node text
at about 6.3 pt, under the band the scaffold’s two diagrams occupy. Shorter
node text — not wordier, which is the fix for a graph that is too NARROW —
took them to 580 and 660 pt and 7.6 to 8.7 pt. `pdfinfo` is not installed
here either; the page size reads out of the PDF’s `/MediaBox` with three
lines of Python, which is what `pdfinfo` prints.

---

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

Two chapters of fourteen are written. The outstanding work is tracked as
GitHub issues under the `chapter`, `appendix`, `experiment` and
`infrastructure` labels — **work from the labels, not from a list here**,
because a list in this file is the class of claim nothing can check. In rough
order:

1. **Chapters 2, 4, 5 and 6**, which with the written Chapters 1, 3 and 7
   complete v0.1. The suggested order was 1, 2, 3 first, because every later
   chapter's listings assume the reader trusts the environment — and two
   chapters written out of that order did not suffer for it, because each
   names what it borrows and borrows almost nothing. Treat the ordering as a
   preference rather than a constraint.
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
