"""The same four lines, under their own name and under the stdlib's.

    cd code && uv run python ch07/shadowing.py

sys.path[0] is the directory of the script being run, and it comes FIRST.
So a file of yours named after a module you import wins, and what `import
random` binds is your file -- which then has no random() on it.

The error names neither the shadowing nor the file that caused it.
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

INNOCENT = Path(__file__).resolve().parent / "shadow" / "innocent.py"


def run_as(name: str) -> str:
    """Copy innocent.py into a scratch directory as `name`, and run it."""
    with tempfile.TemporaryDirectory() as scratch:
        target = Path(scratch) / name
        shutil.copy(INNOCENT, target)
        result = subprocess.run(
            [sys.executable, name],
            cwd=scratch,
            capture_output=True,
            text=True,
        )
    if result.returncode == 0:
        return f"exit 0: {result.stdout.strip()}"
    last = result.stderr.strip().splitlines()[-1]
    return f"exit {result.returncode}: {last}"


def main() -> int:
    for name in ("innocent.py", "random.py"):
        print(f"{name}")
        print(f"  {run_as(name)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
