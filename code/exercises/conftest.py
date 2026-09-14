"""Under PYBOOK_STARTERS=fail every exercise test is a strict xfail.

A starter that passes its own test would then be reported as an unexpected
pass, which pytest counts as a failure -- so `PYBOOK_STARTERS=fail uv run
pytest exercises` exits 0 exactly when every starter still has work in it.
"""

from __future__ import annotations

import os

import pytest


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    if os.environ.get("PYBOOK_STARTERS") != "fail":
        return
    marker = pytest.mark.xfail(
        reason="a starter must fail until the reader finishes it",
        strict=True,
    )
    for item in items:
        item.add_marker(marker)
