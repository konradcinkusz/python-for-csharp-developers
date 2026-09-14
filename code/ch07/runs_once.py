"""One module body, three imports, one object.

    cd code && uv run python ch07/runs_once.py

`import` is not a declaration that a namespace exists. It is a lookup in
sys.modules, and only a miss runs the module's body. Everything in section
7.1 follows from that, including the parts that hurt.
"""

import importlib
import sys

# The miss. greeting.py's body runs here, and prints as it goes.
import greeting


# --8<-- [start:again]
def import_it_again() -> tuple[object, object]:
    """Import the same module twice more, the way another module would."""
    # importlib.import_module is the import statement as a function. It goes
    # through the same cache, so neither of these runs greeting.py's body.
    return (
        importlib.import_module("greeting"),
        importlib.import_module("greeting"),
    )
# --8<-- [end:again]


def main() -> int:
    again, once_more = import_it_again()
    print(f"three names, one object: {greeting is again is once_more}")
    print(f"one entry in the cache:  {greeting is sys.modules['greeting']}")
    print(f"the object knows its name: {greeting.__name__}")
    print(f"and it has a value on it: {greeting.greet('Ada')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
