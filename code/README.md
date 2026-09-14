# code/

Every listing, exercise and measurement in *Python for .NET Engineers*, as
one `uv` project pinned to the versions on the book's title page.

```
src/trace_assert/     the guiding project -- built up from chapter 11
chNN/                 the listings of chapter NN, one file each
exercises/chNN/       starters, and solutions/ beside them; a test per exercise
measure/              the scripts that produce every number the book prints
tests/                runs every listing as a script
```

```bash
uv sync --locked                       # exactly the environment CI has
PYBOOK_SOLUTIONS=1 uv run pytest       # listings + exercise SOLUTIONS
PYBOOK_STARTERS=fail uv run pytest exercises   # every starter must FAIL
uv run ruff check . && uv run pyright  # 79 columns, strict
uv run python measure/ledgers.py       # figures/values/ledgers.tex
```

A reader works an exercise by editing the starter and running
`uv run pytest -k <key>`; CI runs the same test against `solutions/`.

A bare `uv run pytest` therefore runs the exercise tests against the
STARTERS, which fail by design, so on a pristine checkout it is red. That is
the reader's command, not the maintainer's: `PYBOOK_SOLUTIONS=1` is what CI
runs, and this file used to say otherwise.
