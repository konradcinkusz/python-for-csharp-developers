"""Solution 7.3 -- the import is inside the function that needs it.

After the first call it costs a dict lookup in sys.modules, which is what
the import statement is anyway. What it buys is that importing this module
is now free, and that nothing at import time can be in the wrong order.
"""

NAMED = {"red": (1.0, 0.0, 0.0), "lime": (0.0, 1.0, 0.0)}


def to_hsv(name: str) -> tuple[float, float, float]:
    """Convert one of the named colours to hue, saturation, value."""
    import colorsys

    red, green, blue = NAMED[name]
    return colorsys.rgb_to_hsv(red, green, blue)
