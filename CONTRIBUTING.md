# Contributing

The single most useful contribution to this book is an **erratum**: a listing
that no longer runs on the versions the title page names, a C# comparison that
is wrong, a trap the book should catch and does not. Use the
[erratum template](.github/ISSUE_TEMPLATE/erratum.yml) and include the
versions you are running — most reports are version drift rather than
mistakes, and without the versions a report cannot be acted on.

## Working on the book

```bash
git clone https://github.com/konradcinkusz/python-for-csharp-developers.git
cd python-for-csharp-developers
make            # numbers, diagrams, both editions, then the gates
make debt       # every outstanding-work ledger
```

Read `CLAUDE.md` before touching a chapter. It carries the conventions, the
traps already hit, and the reasons behind every mechanism in the repository.

## House rules, in one screen

- **Every listing is a file under `code/`, and every file is run.** A listing
  that has not been executed against the pinned versions carries a
  `verifybox`. Removing the box means you ran the code.
- **Versions live in two places that must agree**: `preamble.tex` (what the
  book prints) and `code/pyproject.toml` (what CI installs).
  `make pins` fails when they differ.
- **Both editions or neither.** A chapter, a listing, an exercise or a diagram
  added to `en/` is added to `pl/` in the same commit; `tools/parity.py`
  fails the build otherwise. Listing comments stay English in both.
- **79 columns** in every `.py` file under `code/`, because that is what fits
  the page without wrapping.
- **Under three thousand words** of prose per chapter. The build counts.
- **ASCII inside listings.** No em dashes or smart quotes in any listing
  environment.
- **Measurements over assertions.** A claim about what is faster comes with a
  script under `code/measure/` and a number, or is labelled as judgement.

## Style

British English and idiomatic Polish, second person, senior audience. The book
is allowed to say a tool is the wrong choice, that a popular idiom is not worth
its cost, and that the author has not verified something. No marketing
register. No *simply*, no *just*, no *powerful*.

## Pull requests

The build runs on every pull request: the code under `code/` on the pinned
versions, the parity checks, both editions, and the cross-reference comparison.
A PR that adds a `\ref` to a label that does not exist, an exercise without a
test, or a listing file that is not there is caught before review.
