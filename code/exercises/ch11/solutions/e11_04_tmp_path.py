"""Reference solution for exercise 11.4."""

from pathlib import Path


def write_report(directory: Path, rows: list[tuple[str, int]]) -> Path:
    """Write report.csv into `directory` and return its path."""
    path = directory / "report.csv"
    path.write_text(
        "".join(f"{sku},{pence}\n" for sku, pence in rows), encoding="utf8"
    )
    return path
