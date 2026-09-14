"""trace-assert: deterministic assertions over an agent's execution trace.

This is the guiding project of *Python for .NET Engineers*. It is a port to
Python of the first layer of agent-eval-bench, and it is built up one stage
per chapter: the trace model and the first two assertions in chapter 11,
trace capture from a real model call in chapter 13, the full assertion set
and packaging in chapter 14.

Stage 01 is three modules and this one. `model` is what a run leaves behind,
`assertions` is what a test says about it, and `plugin` is the one fixture
that hands a test a place to record. Everything a reader imports is
re-exported here, so the package's surface is one import line and its layout
is free to change under it — which it did: chapter 13's stage 02 was written
while the scaffold still had the whole model in THIS file, and its model
call pair now sits in `model` beside the tool pair, with every importer
unchanged because they all came through here.

Every public name is a claim about the finished package, so the surface is
kept as small as the chapters have earned. The remaining assertion types are
defined in agent-eval-bench's own scenario schema and are chapter 14's to
port; none of them is named here, because a list written from memory is the
one thing the guiding project cannot afford.
"""

from __future__ import annotations

from .assertions import assert_tool_called, assert_tool_not_called
from .model import Event, Recorder, Trace

__all__ = [
    "Event",
    "Recorder",
    "Trace",
    "__version__",
    "assert_tool_called",
    "assert_tool_not_called",
]

__version__ = "0.0.2"
