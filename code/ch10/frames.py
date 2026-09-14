"""polars, for the reflex that reaches for LINQ over a table.

A LazyFrame is IQueryable: the chain below builds a plan and reads nothing.
`collect()` is `ToList()`. In between, an optimiser rewrites the plan, so
the filter reaches the file rather than the file reaching the filter --
which is the whole of why IQueryable was worth having over IEnumerable.

An expression -- pl.col("severity") <= 2 -- is an object describing a
comparison, not a lambda over a row. That is an expression tree by another
name, and it is there for the same reason: something other than Python has
to be able to read it and turn it into a plan.

Run it from code/:

    uv run python ch10/frames.py
"""

# polars 1.44.2 does not type-check strictly: its LazyFrame methods are
# annotated with unions wide enough that pyright calls the result
# partially unknown. The checker is right and the stubs are the reason,
# so the suppression is here, named, rather than a blanket relaxation of
# the project's strict mode. Chapter 3 is where this class of problem
# belongs; this is one instance of it, recorded at the call site.
# pyright: reportUnknownMemberType=false

from __future__ import annotations

import tempfile
from pathlib import Path

import polars as pl
from model import ROWS

Row = tuple[str, int]

# --8<-- [start:lazy]


def lost_minutes(frame: pl.LazyFrame) -> pl.LazyFrame:
    """Nothing in here touches a row. It returns a plan."""
    return (
        frame.filter(pl.col("severity") <= 2)
        .group_by("service")
        .agg(pl.col("minutes").sum().alias("lost"))
        .sort("lost", descending=True)
    )


# --8<-- [end:lazy]

# --8<-- [start:collect]


def report(csv: Path) -> tuple[list[Row], bool]:
    """Build, then run -- and ask the plan what it decided to do.

    SELECTION: on the scan node is the filter pushed down into the reader,
    so rows that fail it are never decoded. That is the optimisation an
    IQueryable exists to make and an IEnumerable cannot.
    """
    plan = lost_minutes(pl.scan_csv(csv))
    pushed = "SELECTION:" in plan.explain()
    rows = [(str(s), int(m)) for s, m in plan.collect().rows()]
    return rows, pushed


# --8<-- [end:collect]


def write_csv(path: Path) -> None:
    lines = ["service,severity,minutes"]
    lines += [f"{name},{sev},{mins}" for name, _, sev, mins in ROWS]
    path.write_text("\n".join(lines) + "\n", encoding="utf8")


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        csv = Path(tmp) / "incidents.csv"
        write_csv(csv)
        plan = lost_minutes(pl.scan_csv(csv))
        print(f"before collect: {type(plan).__name__}")
        print(f"after collect:  {type(plan.collect()).__name__}")
        rows, pushed = report(csv)
        print(f"filter pushed into the scan: {pushed}")
        print(f"report: {rows}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
