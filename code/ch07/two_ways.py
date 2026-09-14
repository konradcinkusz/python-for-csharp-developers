"""The same file, run two ways, answering differently.

    cd code && uv run python ch07/two_ways.py

`python shop/where.py` puts the file's OWN directory at the head of
sys.path and gives the module no package. `python -m shop.where` puts the
current directory there and imports it as part of `shop`. The src/ layout of
chapter 2 is that difference, taken seriously.
"""

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def run(*args: str) -> str:
    """Run the interpreter with `args` from ch07/, and return its output."""
    result = subprocess.run(
        [sys.executable, *args],
        cwd=HERE,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.rstrip("\n")


def main() -> int:
    print("python shop/where.py")
    print(run("shop/where.py"))
    print()
    print("python -m shop.where")
    print(run("-m", "shop.where"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
