"""Exercise 11.4: tmp_path is the directory, and the test owns it."""

from pathlib import Path

from exercises._loader import load

ROWS = [("SKU-1", 750), ("SKU-2", 1000)]


def test_it_writes_report_csv_where_it_was_told(tmp_path: Path) -> None:
    written = load("ch11", "e11_04_tmp_path").write_report(tmp_path, ROWS)
    assert written == tmp_path / "report.csv"
    assert written.read_text(encoding="utf8") == "SKU-1,750\nSKU-2,1000\n"


def test_it_writes_nothing_else(tmp_path: Path) -> None:
    load("ch11", "e11_04_tmp_path").write_report(tmp_path, ROWS)
    assert [p.name for p in tmp_path.iterdir()] == ["report.csv"]


def test_an_empty_report_is_an_empty_file(tmp_path: Path) -> None:
    written = load("ch11", "e11_04_tmp_path").write_report(tmp_path, [])
    assert written.read_text(encoding="utf8") == ""
