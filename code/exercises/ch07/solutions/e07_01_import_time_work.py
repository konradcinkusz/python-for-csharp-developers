"""Solution 7.1 -- the same work, at call time.

The module body now binds two things: a constant that is genuinely
constant, and a function. Importing it costs a dict literal and a function
object, which is what importing anything should cost.
"""

import os

DEFAULTS = {"region": "eu-west-1", "retries": "3"}


def build_settings() -> dict[str, str]:
    """Read the environment now, not at import time."""
    return {
        key: os.environ.get(f"PYBOOK_{key.upper()}", default)
        for key, default in DEFAULTS.items()
    }
