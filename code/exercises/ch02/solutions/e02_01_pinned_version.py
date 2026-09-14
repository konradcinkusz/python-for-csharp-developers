"""Exercise 2.1, solved."""

from typing import Any


def pinned(lock: dict[str, Any], name: str) -> str:
    """Return the version `lock` pins `name` to."""
    wanted = name.lower()
    packages: list[dict[str, Any]] = lock.get("package", [])
    for package in packages:
        if str(package["name"]).lower() == wanted:
            return str(package["version"])
    # Not `return None`, and not an empty string: both would let a caller
    # carry on with a version that does not exist. The lock is the
    # authority, so being absent from it is an error rather than a value.
    raise KeyError(name)
