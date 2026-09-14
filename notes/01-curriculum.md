# 01 — The curriculum

Why these fourteen chapters, in this order, at this length; what each part
buys; where the book stops and the companion volumes start; the experiments
and which of them have run; the guiding project; and the release plan.

The chapter sequence, every brief and the dependency graph live in
`tools/chapters.json`. **This file does not repeat them.** A second copy of a
brief is the next thing to go stale, and the companion books each paid for
one. Read a brief with:

```bash
python3 -c "import json; m=json.load(open('tools/chapters.json')); \
  [print(c['id'], c['en'], '<-', c['deps']) for c in m['chapters']]"
```

## 1. The reader, and the one sentence the book rests on

A senior C# engineer who has to read, write and ship Python — because the
team's AI work is in Python, because a service they own was rewritten, or
because the next job asks for it. They do not need to be taught what a loop
is. **They have a mental model that is mostly right and wrong in a few
specific places, and the places are where the incidents come from.**

So the unit of teaching is a *mapping*: one thing the reader already knows,
set beside its Python counterpart, with the difference elicited before it is
named. A chapter that explains Python from nothing has failed its reader
twice — once by boring them and once by never reaching the place their
habit breaks.

Three things the book is not, each because something else already is:

- **Not a Python-from-zero course.** The reader can read code on page one.
- **Not a library catalogue.** Each tool appears once, where its .NET
  counterpart is, and the tool matrix (Appendix C) is the only place they are
  all listed.
- **Not another AI book.** Agents, tools, graphs and middleware belong to
  *LangChain, LangGraph and Async Python*. This book stops at one model call
  and one structured output, in Chapter 13, and points there.

## 2. The five parts

| Part | Question it answers | Why here |
|---|---|---|
| I Runtime and toolchain | What am I running, and how do I get a reproducible environment? | Every later chapter's listings run under `uv`; the reader has to trust the harness before the language |
| II The language, mapped | Which of my C# reflexes hold, and which fail silently? | The dictionary proper: objects, functions, errors, imports |
| III Concurrency | I know `Task`. What transfers? | One chapter, deliberately: the depth is the LangChain book's and this is the translation view |
| IV Shipping | How do I put it in production without unlearning what I know about services, data, tests and ops? | The field manual; the four chapters map four frameworks onto four the reader already runs |
| V Python for AI work | What does the AI toolchain assume I already know? | The bridge to the next volume, and the guiding project's finish |

Part I before Part II is the one ordering decision worth defending. The
obvious order is language first, toolchain second. It is wrong for this
reader for the same reason the math book put floating point before linear
algebra: the reader will type every listing into an environment, and an
environment that is a directory rather than a machine setting is the first
habit that breaks. Chapter 2's own repository skeleton is `code/`, which CI
runs on every push, so the reader is handed a verified environment before
they are asked to trust a listing.

Part III is one chapter and that is a scope decision, not an estimate. The
LangChain book's Chapters 3 and 4 own the event loop, cancellation and the
measurements in depth; Chapter 8 here is the TPL-to-asyncio translation table
and the three incidents, and it points there in one sentence. Two books that
each explain `gather` are a defect.

## 3. Scope discipline

- **Fourteen chapters, each under 3,000 words of prose.** The gate is
  `tools/check_structure.py --words`, which counts words a reader reads
  (no comments, no listings, no macro names) and fails a written chapter over
  budget. Listings and exercises are not prose and do not count; a chapter
  that is mostly listings is what this book wants.
- **Each chapter publishable separately.** A chapter names what it borrows
  from earlier chapters and declares what it defers, so a reader can start at
  Chapter 8 with Chapter 1 unread.
- **Every listing runs in CI on pinned versions**, or carries a `verifybox`
  saying it has not. `make debt` counts the boxes; Appendix E prints the
  count for a reader who cannot run `make`.
- **Every exercise is three files**: a starter that must *fail* its test, a
  solution that must *pass* it, and the test. `make code` runs the solutions;
  `make starters` runs the starters under a strict expected-failure marker,
  so an exercise whose starter accidentally passes is a build failure. That
  is what makes *PDF on the left, IDE on the right* a mechanically checked
  claim rather than a hope.
- **Two to four figures per chapter**, Mermaid, one source per language,
  rendered in CI. Nothing is a screenshot.

## 4. Experiments

Eight are specified, all free, none needing a provider or a budget. Every
claim an experiment would support stays labelled as judgement until it runs.
**Fill the Status column in the pass that runs the experiment, and never
restate a total here or in `CLAUDE.md`** — the math book's ledger said
"none has been run" for five programs after one had.

| # | Chapter | What | Cost | Status |
|---|---|---|---|---|
| E1 | 1 | CPU-bound work, four threads, default build against `python3.14t`, on the pinned interpreter | free; needs the free-threaded build installed by `uv python install 3.14t` | not run |
| E2 | 2 | Cold `uv sync` against `pip install -r` on the same lockfile | free | **run**, Ch. 2 pass, September 2026: `code/measure/e2_install.py`, raw trials committed beside it. The finding is the cache column, not the headline — a warm cache buys uv a factor of nine and buys pip nothing, because pip's time is its own work rather than the download |
| E3 | 6 | Cost of a `try` against a check, happy path and unhappy path | free | not run |
| E4 | 8 | One blocking call's degradation, in the TPL-against-asyncio framing | free; the LangChain book's Chapter 3 has the asyncio half already | not run |
| E5 | 9 | uvicorn workers against concurrency: throughput, p50, p95, mocked upstream, calibrated the way the LangChain book's Chapter 13 recorded | free | not run |
| E6 | 10 | The N+1 reproduced and counted from the engine's echo, before and after `selectinload`, on SQLite | free | not run |
| E7 | 12 | Image size and cold start of three Dockerfile shapes | free; needs Docker, so CI rather than the sandbox | not run |
| E8 | 13 | Validation cost of one structured output across pydantic strict, pydantic lax and a dataclass over `json` | free | not run |

Each result goes into `code/measure/<experiment>.py`, which writes
`figures/values/<experiment>.tex`; the chapter reads it with `\val{}` and
`make verify` fails when the two drift. **A timing cannot be re-derived on
every machine, so an experiment that measures one splits in two**: a `--run` mode
that performs the benchmark and writes committed raw data under
`code/measure/data/`, and a default mode that only formats that data into the
value file. CI runs the second, which is deterministic; the first is run by hand
and reviewed as a diff. E2 is the first to need this and the shape is general. The three companion books' rule
holds here without exception: **a number the reader cannot do in their head
is computed, never typed**, and a machine-dependent residual is committed as
a bound, never as a figure.

The two methodological errors the LangChain book made running its service
benchmark — load driver and server on one event loop, and a client that
saturated before the server did — are the first two things to check before
E5 is believed.

## 5. The guiding project: `trace-assert`

A Python port of the first layer of
[agent-eval-bench](https://github.com/konradcinkusz/agent-eval-bench):
deterministic assertions over an execution trace, expressed as pytest
fixtures and functions. It is the book's one running thread and it exists
for three reasons: the reader ships a package by the end; the same
instrument exists in .NET and TypeScript, so Chapter 14 can compare three
ports of one design; and the book's own CI runs it from the scaffold
onward, which is what makes the *tests pass without a model* rule
verifiable rather than stated.

| Stage | Chapter | Adds |
|---|---|---|
| skeleton | scaffold | `Event(kind, name, payload)`, `Trace(events)` with `of_kind` and `names`; one test |
| 01 | 11 | the `trace` fixture and the first two assertions, with failure messages that name the offending event |
| 02 | 13 | recording a model call as trace events, from the Chapter 13 client |
| final | 14 | the full assertion set, packaged with `uv build`, published by trusted publishing |

**The assertion list is agent-eval-bench's, and it must be copied from that
project's specification when Chapter 14 is written, never reconstructed from
memory.** The count is whatever that specification says. This note
deliberately does not list them, because a list written here from
recollection would be the next thing to go stale, and the whole point of the
project is that three ports implement one design.

The rule that keeps the stages honest is the LangChain book's: every stage's
tests pass with no network, no database server and no model.

## 6. Overlap rules against the companion volumes

Recorded once, here, because every brief carries its own and the sum is what
matters. The trilogy is one book in three volumes, so a topic has exactly one
owner.

| Topic | Owner | This book |
|---|---|---|
| The GIL and the runtime model | this book, Ch. 1 | — |
| The GIL's consequence for an event loop | LangChain Ch. 3 | one sentence in Ch. 1 |
| The toolchain table | this book, Ch. 2 | the LangChain book's half-page table should point back here once v0.1 ships |
| Type hints, checkers, `Protocol` | this book, Ch. 3 | pydantic in depth is Ch. 9 and Ch. 13 |
| Decorators as a mechanism | this book, Ch. 5 | agent middleware as a use is LangChain Ch. 7 |
| Exceptions, EAFP, `ExceptionGroup` | this book, Ch. 6 | cancellation and timeouts are LangChain Ch. 4 and are **not** here |
| The event loop, `gather`, cancellation, the measurements | LangChain Ch. 3 and 4 | Ch. 8 is the translation view and never repeats a section |
| FastAPI as a framework | this book, Ch. 9 | serving agents over SSE is LangChain Ch. 13 |
| Agents, tools, graphs, middleware | LangChain, all of Parts II and III | Ch. 13 stops at one model call and one structured output |
| Microsoft Agent Framework | maf-book | not mentioned beyond the trilogy note |

## 7. Releases

| Release | Parts | Chapters | Appendices |
|---|---|---|---|
| v0.1 | I and II | 1 to 7 | — |
| v0.2 | III and IV | 8 to 12 | — |
| v1.0 | V | 13 and 14 | A to E |

The manifest carries each chapter's release; `release.yml` builds and
attaches both PDFs to a tag. A release is cut when every chapter in it has
no `verifybox`, every one of its exercises passes both the solution run and
the starter run, and its experiments have run or their claims are labelled.

## 8. Decisions taken at the scaffold, and two left open

- **pytest is pinned at 9.1.1, not 8.** The brief said pytest 8; the current
  release on the day the pins were verified is 9.1.1, and pinning a major
  behind on day one would have the reader install something the book was not
  run on. The pin table in `preamble.tex` is the record.
- **One-sided A4, `openany`.** The book is read on a screen beside an IDE, so
  mirrored margins and blank versos are a print convention that costs the
  reader page turns and buys nothing.
- **Appendix E is generated.** The brief had four appendices; the manifest
  ledgers the math book learned to print for the reader needed a fifth, and it
  is computed by `code/measure/ledgers.py` rather than written.
- **Open: whether CI compiles the C# side of Appendix D.** Every Python
  solution has a test CI runs. The C# solutions are listings too, and
  compiling them needs a .NET SDK in the workflow. Recorded in `CLAUDE.md`;
  decide before Appendix D is written.
- **Open: the free-threaded interpreter in CI.** E1 needs `python3.14t`. `uv`
  can install it, but whether the `code` job installs two interpreters or E1
  runs in a job of its own is undecided.
