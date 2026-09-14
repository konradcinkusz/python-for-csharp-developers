"""Exercise 2.2 -- what does a deployment actually install?

`[project].dependencies` is what the thing needs to RUN.
`[dependency-groups]` is what you need to WORK on it. A container that
ships pytest and ruff is shipping a test runner to production, and the
split is the only thing standing between you and that.

Make `install_set` return the set of DISTRIBUTION NAMES a given selection
of groups would install: always the runtime dependencies, plus the members
of each named group. Names only -- no version specifiers, no extras, no
environment markers -- and lowercased, because `SQLAlchemy` and
`sqlalchemy` are one project.
"""

from collections.abc import Iterable
from typing import Any


def install_set(
    pyproject: dict[str, Any], groups: Iterable[str] = ()
) -> set[str]:
    """Distribution names installed by the runtime deps plus `groups`.

    A requirement can be written "pydantic", "pydantic==2.13.5",
    "httpx[http2]>=0.28", or "pytest ; python_version >= '3.14'". Only the
    name is wanted.

    Raise KeyError(group) for a group the file does not define, because a
    typo in a group name that silently installs nothing is exactly the
    kind of thing that is discovered in production.
    """
    raise NotImplementedError("your turn: replace this line")
