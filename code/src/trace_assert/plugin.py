"""The `trace` fixture, as a pytest plugin module.

A plugin is a module pytest is told about; a fixture in it is then available
to every test without an import. Stage 01 asks for it the way a reader
would, with one line in the rootdir conftest.py:

    pytest_plugins = ["trace_assert.plugin"]

Chapter 14 turns that line into a `pytest11` entry point in the package's
own metadata, at which point installing trace-assert is enough and no
conftest is needed. The line is the staging, not a workaround: the entry
point is packaging, and packaging is chapter 14's.

The book's own code/ project keeps the conftest line, and chapter 14
measures why: that project is named after the BOOK and is not a
publishable trace-assert, so declaring the entry point there would
register the plugin for anyone who installed fourteen chapters of
listings.
"""

from __future__ import annotations

import pytest

from .recorder import Recorder

__all__ = ["trace"]


@pytest.fixture
def trace() -> Recorder:
    """A fresh Recorder per test.

    Function-scoped on purpose, and it is the scope every assertion in this
    package assumes: a trace shared between two tests is two runs' evidence
    in one place, and the count assertions would then be counting the
    neighbour's calls as well.
    """
    return Recorder()
