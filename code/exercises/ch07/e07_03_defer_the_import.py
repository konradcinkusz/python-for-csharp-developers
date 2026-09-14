"""Exercise 7.3 -- pay for an import when it is used, not when it is read.

This module imports colorsys at the top and uses it in one function that
most callers never reach. In a real package that import is the one that
closes a cycle, or the one that adds two hundred milliseconds to the start
of a command-line tool that was not going to touch it.

Move the import inside to_hsv, so that importing this module does not
import colorsys and calling to_hsv does. The test checks the cache before
and after, so a module-level import cannot pass it.
"""

import colorsys

NAMED = {"red": (1.0, 0.0, 0.0), "lime": (0.0, 1.0, 0.0)}


def to_hsv(name: str) -> tuple[float, float, float]:
    """Convert one of the named colours to hue, saturation, value."""
    red, green, blue = NAMED[name]
    return colorsys.rgb_to_hsv(red, green, blue)
