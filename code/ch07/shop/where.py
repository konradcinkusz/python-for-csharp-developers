"""What the interpreter thinks this file is, and who its parent is.

The answers are different under the two ways of running it, and the
difference is the whole of why `python -m` exists:

    cd code && uv run python ch07/shop/where.py       # a file
    cd code && uv run python -m shop.where            # a module in a package

Run ch07/two_ways.py to see both at once.
"""

import sys
from pathlib import Path


# --8<-- [start:relative]
def _relative_import() -> str:
    """A relative import is resolved against __package__, so it needs the
    interpreter to know which package this module belongs to. Run as a file
    it does not, and that is an ImportError rather than a missing file."""
    try:
        from . import discount
    except ImportError as exc:
        return f"{type(exc).__name__}: {exc}"
    return f"worked, discount.RATE is {discount.RATE}"


RELATIVE = _relative_import()
# --8<-- [end:relative]


def report() -> str:
    """Three lines: the name, the package, and the head of sys.path."""
    # The directory name only: the absolute path is this machine's, and a
    # transcript that carries one goes stale on somebody else's.
    head = Path(sys.path[0]).name
    return (
        f"  __name__     {__name__}\n"
        f"  __package__  {__package__!r}\n"
        f"  sys.path[0]  .../{head}\n"
        f"  relative import\n    {RELATIVE}"
    )


if __name__ == "__main__":
    print(report())
