"""Exercise 2.2, solved."""

from collections.abc import Iterable
from typing import Any

# Everything that can end a distribution name and start something else:
# a version specifier, an extras list, or an environment marker.
_TERMINATORS = "=<>!~[; "


def _name(requirement: str) -> str:
    for i, char in enumerate(requirement):
        if char in _TERMINATORS:
            return requirement[:i].strip().lower()
    return requirement.strip().lower()


def install_set(
    pyproject: dict[str, Any], groups: Iterable[str] = ()
) -> set[str]:
    """Distribution names installed by the runtime deps plus `groups`."""
    project: dict[str, Any] = pyproject.get("project", {})
    runtime: list[str] = project.get("dependencies", [])
    names = {_name(requirement) for requirement in runtime}

    defined: dict[str, list[str]] = pyproject.get("dependency-groups", {})
    for group in groups:
        if group not in defined:
            raise KeyError(group)
        names |= {_name(requirement) for requirement in defined[group]}
    return names
