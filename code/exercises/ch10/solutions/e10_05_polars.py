"""Reference solution for exercise 10.5.

Every step here is an expression rather than a lambda, which is what lets
polars read the chain and rewrite it. Nothing is read until collect().
"""

# polars 1.44.2's LazyFrame methods are annotated with unions wide
# enough that pyright calls the chained result partially unknown. The
# checker is right and the stubs are the reason; ch10/frames.py carries
# the same named suppression and the chapter says why.
# pyright: reportUnknownMemberType=false

from __future__ import annotations

import polars as pl


def lost_minutes(frame: pl.LazyFrame) -> pl.LazyFrame:
    """Minutes lost per service, severity 2 or worse, heaviest first."""
    return (
        frame.filter(pl.col("severity") <= 2)
        .group_by("service")
        .agg(pl.col("minutes").sum().alias("lost"))
        .sort("lost", descending=True)
    )
