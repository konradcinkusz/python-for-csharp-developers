"""There is a compile step. This is it.

    cd code && uv run python ch01/bytecode.py

Python compiles source to bytecode before it runs anything, exactly as C#
compiles to IL -- the difference is when, and where the result is kept. The
compiler runs on import, the result goes in __pycache__ beside the source,
and `dis` is the tool that shows it, the way ildasm shows IL.
"""

import dis
import importlib.util
import sys


# --8<-- [start:function]
def total_due(subtotal: float, rate: float) -> float:
    tax = subtotal * rate
    total = subtotal + tax
    return round(total, 2)
# --8<-- [end:function]


def main() -> int:
    dis.dis(total_due)
    print()
    # Where the compiler would put this module's bytecode if it were
    # imported rather than run. A relative name on purpose: the real call
    # takes __file__ and returns an absolute path, which is a fact about
    # this machine rather than about Python.
    print("cached at:", importlib.util.cache_from_source("widget.py"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
