"""D.16 -- read a dotted path out of nested dictionaries.

This is the shape every configuration reader has. The isinstance guard is
the part that is not optional: without it a path that runs into a string
or a list raises TypeError instead of returning the default, which is the
bug the tests catch.

Run it from code/:

    uv run python appd/p16_deep_get.py
"""

from __future__ import annotations

from typing import cast


# --8<-- [start:solution]
def deep_get(data: object, path: str, default: object = None) -> object:
    """data['a']['b']['c'] for path 'a.b.c', or default at any miss.

    The cast is the one Chapter 3 argues for: isinstance narrows to
    dict[Unknown, Unknown], not dict[str, object], so strict pyright
    reports the return as partially unknown without it. One widening, at
    the boundary, said out loud.
    """
    current = data
    for key in path.split("."):
        if not isinstance(current, dict):
            return default
        mapping = cast(dict[str, object], current)
        if key not in mapping:
            return default
        current = mapping[key]
    return current
# --8<-- [end:solution]


def main() -> int:
    config = {"db": {"primary": {"port": 5432}}}
    print(deep_get(config, "db.primary.port"))
    print(deep_get(config, "db.replica.port", 0))
    print(deep_get(config, "db.primary.port.deeper", "missed"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
