"""The first listing in the book, and the shape every later one has.

Run it from the repository root:

    cd code && uv run python ch00/loop.py

It prints which interpreter ran it and whether that interpreter carries the
global interpreter lock -- the two facts chapter 1 starts from. Both are read
from the interpreter rather than written down, which is the rule every
listing in this book follows: nothing in a listing is a claim the listing
did not check.
"""

import sys


def describe_interpreter() -> str:
    """One line: the version, and whether the GIL is enabled."""
    version = ".".join(str(part) for part in sys.version_info[:3])
    # sys._is_gil_enabled() exists from Python 3.13 and answers False only
    # on the free-threaded build (python3.14t). On the default build it is
    # True, and chapter 1 measures what that costs.
    gil = sys._is_gil_enabled()  # noqa: SLF001 -- it is the documented probe
    return f"Python {version}, GIL enabled: {gil}"


if __name__ == "__main__":
    print(describe_interpreter())
