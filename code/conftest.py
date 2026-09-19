"""The rootdir conftest: one line, and it is chapter 11's subject.

`pytest_plugins` registers a plugin module for the whole session, and it is
ONLY read in the rootdir conftest -- pytest refuses it in a nested one, and
says so, because a plugin that appears half way down a tree would apply to
tests collected before it was found.

This is how a reader wires trace-assert into their own suite until chapter
14 gives the package a `pytest11` entry point of its own.
"""

pytest_plugins = ["trace_assert.plugin"]
