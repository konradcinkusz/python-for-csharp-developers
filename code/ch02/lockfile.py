"""A declaration is not a lock, and the gap is most of the environment.

Run it from code/:

    uv run python ch02/lockfile.py

It reads this book's own two files -- pyproject.toml, which is what a
person wrote, and uv.lock, which is what uv resolved -- and counts them
against each other. Both are TOML, and tomllib has been in the standard
library since 3.11, so this needs nothing installed.

The numbers are not typed anywhere. Change a dependency and re-run it and
they move, which is the only way a count in a book stays true.

The `dict[str, Any]` annotations are the honest shape of a parsed TOML
document and not laziness: tomllib cannot know what is in the file, so the
claim "this key holds a list of strings" is the reader's, made where the
value is used. Chapter 3 is about what a checker does and does not do with
that admission.
"""

import sys
import tomllib
from pathlib import Path
from typing import Any

CODE = Path(__file__).resolve().parent.parent


def requirement_name(requirement: str) -> str:
    """Turn "pydantic==2.13.5" into "pydantic".

    The name runs up to the first character that starts a version
    specifier, an extra or an environment marker.
    """
    for i, char in enumerate(requirement):
        if char in "=<>!~[; ":
            return requirement[:i].strip().lower()
    return requirement.strip().lower()


def declared(pyproject: dict[str, Any]) -> set[str]:
    """Every distribution a person named, across both tables.

    `[project].dependencies` is what the thing needs to RUN.
    `[dependency-groups]` is what you need to WORK on it, and the two
    being separate lists is the whole point of the split.
    """
    project: dict[str, Any] = pyproject.get("project", {})
    runtime: list[str] = project.get("dependencies", [])
    groups: dict[str, list[str]] = pyproject.get("dependency-groups", {})

    names = {requirement_name(r) for r in runtime}
    for members in groups.values():
        names |= {requirement_name(m) for m in members}
    return names


def locked(lock: dict[str, Any]) -> set[str]:
    """Every distribution uv resolved, which is the whole graph."""
    packages: list[dict[str, Any]] = lock.get("package", [])
    return {str(package["name"]).lower() for package in packages}


def main() -> int:
    pyproject: dict[str, Any] = tomllib.loads(
        (CODE / "pyproject.toml").read_text(encoding="utf8")
    )
    lock: dict[str, Any] = tomllib.loads(
        (CODE / "uv.lock").read_text(encoding="utf8")
    )

    named = declared(pyproject)
    resolved = locked(lock)
    # The project itself is in the lock and was nobody's dependency, so it
    # belongs on neither side of the comparison.
    project: dict[str, Any] = pyproject["project"]
    resolved.discard(str(project["name"]).lower())

    print(f"distributions a person named:  {len(named)}")
    print(f"distributions uv.lock pins:    {len(resolved)}")
    print(f"nobody named, uv worked out:   {len(resolved - named)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
