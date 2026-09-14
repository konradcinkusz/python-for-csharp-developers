"""Exercise 10.5 -- build the plan, do not run it.

Return minutes lost per service for incidents of severity 2 or worse,
heaviest first, as a LazyFrame.

The test checks the rows AND that what you returned is still a plan. A
function that ends in .collect() has done the work before its caller asked
for it, which is the difference between IQueryable and IEnumerable and the
reason polars has two types.
"""

from __future__ import annotations

import polars as pl


def lost_minutes(frame: pl.LazyFrame) -> pl.LazyFrame:
    """Minutes lost per service, severity 2 or worse, heaviest first."""
    raise NotImplementedError("your turn: return the plan, not the rows")
