"""A module whose body does work, so that importing it is visibly not free.

Run it on its own and the body runs once:

    cd code && uv run python ch07/greeting.py

Import it three times from runs_once.py and the body still runs once. That
is the whole of section 7.1: a module is an object, and `import` is the
expression that builds it exactly once.
"""

import os

# Module level. This runs when the module is first imported -- not when
# anything in it is called, and not again on the second import.
print("greeting.py: the body is running")

# A C# static field initialiser is the closest thing, and it is not close:
# this one reads the environment at import time, so which value it holds
# depends on when the first import happened.
SALUTATION = os.environ.get("PYBOOK_SALUTATION", "Hello")


def greet(name: str) -> str:
    """Greet `name` with whatever the environment said at import time."""
    return f"{SALUTATION}, {name}"


if __name__ == "__main__":
    print(greet("Ada"))
