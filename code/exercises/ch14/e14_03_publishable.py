"""Exercise 14.3 -- the last one: make it publishable.

`uv build` will build almost anything. What decides whether an upload is
accepted, and whether anyone can use what they downloaded, is the
`[project]` table -- and the book's own code/ project is not a publishable
`trace-assert`: it is named after the book, it pins one Python minor
because the book runs on exactly one, and it declares runtime
dependencies that the package imports none of.

Return the `[project]` table a published `trace-assert` needs, as TOML
text. The test beside this file parses it with `tomllib` and asks seven
things of it -- read the test; it is the specification.

Three of the seven are worth knowing before you start:

  * `dependencies` must be absent or empty. Every import in
    `src/trace_assert/` is from the standard library, and a package that
    declares what it does not use installs it into everybody's
    environment.
  * `requires-python` must admit more than the one minor the book is
    built on. A library that pins a single minor is a library nobody can
    depend on.
  * the `trace` fixture has to arrive with the install. Chapter 11 got
    it into the suite with a line of conftest.py, which a package
    cannot ask of its users; a `pytest11` entry point is what replaces
    that line.

Then the publish itself is two commands and no secret:

    uv build
    uv publish --trusted-publishing automatic
"""

from __future__ import annotations


def project_table() -> str:
    """Return the [project] table for a publishable trace-assert."""
    raise NotImplementedError("your turn: replace this line")
