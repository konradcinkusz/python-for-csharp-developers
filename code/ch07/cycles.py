"""A cycle that survives, a cycle that does not, and three ways out.

    cd code && uv run python ch07/cycles.py

The cycle is never the error. What fails is a name needed from a module
whose body has not reached the line that binds it -- and `from x import y`
asks for exactly that, at import time, which is why it is the form that
breaks.

The last pair is the same fault in a different place on disk, and CPython
diagnoses the two differently. That is section 7.3's finding and it is why
this file runs both.
"""

import importlib
import sys
import textwrap
from pathlib import Path

HERE = Path(__file__).resolve().parent


def tidy(message: str) -> str:
    """CPython's message, folded to the width of a printed page.

    Verbatim except for two things, both of which would otherwise make the
    output this machine's rather than anybody's: the directory this file
    sits in is taken off the front of any path, and the result is wrapped.
    """
    flat = message.replace(f"{HERE}/", "")
    return textwrap.fill(
        flat, width=74, initial_indent="  ", subsequent_indent="    "
    )


# --8<-- [start:survives]
def cycle_that_survives() -> str:
    """Import the module; read the name off it when it is wanted.

    The module OBJECT exists from the moment its import begins, so binding
    it is always safe. Only an attribute needs the body to have got that
    far, and by the time anything calls describe(), it has.
    """
    from cycle import _orders_fixed

    return _orders_fixed.describe(19.99)
# --8<-- [end:survives]


# --8<-- [start:breaks]
def cycle_that_breaks() -> str:
    """Import the NAME, at import time, in both directions."""
    try:
        importlib.import_module("cycle._orders")
    except ImportError as exc:
        return tidy(f"{type(exc).__name__}: {exc}")
    return "  no error, which would mean this demonstration is broken"
# --8<-- [end:breaks]


# --8<-- [start:flat]
def same_cycle_flat() -> str:
    """The same fault, in two files beside the script rather than in a
    package -- which is the shape a first Python project takes."""
    try:
        importlib.import_module("_flat_orders")
    except ImportError as exc:
        return tidy(f"{type(exc).__name__}: {exc}")
    return "  no error, which would mean this demonstration is broken"
# --8<-- [end:flat]


def cycle_extracted() -> str:
    """The third way out: both sides import a third module instead."""
    from cycle import _orders_extracted

    return _orders_extracted.describe(19.99)


def main() -> int:
    print("import the module, read the name later:")
    print(f"  {cycle_that_survives()}")
    print()
    print("import the name at import time, inside a package:")
    print(cycle_that_breaks())
    print()
    print("the same cycle, flat, in the directory you ran from:")
    print(same_cycle_flat())
    print()
    print("extract what both sides wanted:")
    print(f"  {cycle_extracted()}")
    print()
    left = sorted(n for n in sys.modules if n.startswith("cycle."))
    print(f"modules the cycle package left in the cache: {len(left)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
