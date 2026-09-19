"""The rate a real service would read from configuration.

It exists to be substituted. Chapter 11 patches it twice -- once in the
place it is defined, which does nothing, and once in the place it is looked
up, which works -- and the two modules are separate for exactly that reason.
"""


def vat_rate_percent() -> int:
    """The rate this deployment charges. Deterministic on purpose."""
    return 20
