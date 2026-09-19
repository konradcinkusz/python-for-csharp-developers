"""Exercise 11.4 -- write a file, and let the test own the directory.

Implement `write_report`. It takes a directory and a list of (sku, pence)
pairs, writes `report.csv` inside that directory with one `sku,pence` line
per pair and no header, and returns the path it wrote.

Do not create the directory, do not clean it up and do not pick its name:
the test passes `tmp_path`, and a function that decides where its output
goes cannot be tested without touching the machine it runs on.
"""

from pathlib import Path


def write_report(directory: Path, rows: list[tuple[str, int]]) -> Path:
    """Write report.csv into `directory` and return its path."""
    raise NotImplementedError("your turn: replace this line")
