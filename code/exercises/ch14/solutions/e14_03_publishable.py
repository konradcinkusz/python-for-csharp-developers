"""Reference solution for exercise 14.3."""

from __future__ import annotations


def project_table() -> str:
    """Return the [project] table for a publishable trace-assert."""
    return """
[project]
name = "trace-assert"
version = "0.1.0"
description = "Deterministic assertions over an agent execution trace"
readme = "README.md"
requires-python = ">=3.11"
license = "MIT"

[project.entry-points.pytest11]
trace_assert = "trace_assert.plugin"

[project.urls]
Source = "https://github.com/konradcinkusz/trace-assert"
"""
