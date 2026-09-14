"""An environment is a directory. This prints the directory.

Run it from code/:

    uv run python ch02/where_am_i.py

Nothing here is written down: every line is read back out of the running
interpreter, so the answers are about the interpreter that ran the file
rather than about the one whoever wrote it had.

What is printed is deliberately structural -- a yes or no, and one path
RELATIVE to sys.prefix. An absolute path names a machine, and the whole
claim of the chapter is that the same answers come out of the same
repository on anybody's machine. The book's build re-runs this file and
fails if the output moves, which a path carrying a home directory would do
on every machine it ever ran on.
"""

import sys
from pathlib import Path


def inside_environment(path: str) -> bool:
    """Is `path` under sys.prefix -- that is, inside this environment?"""
    return Path(path).is_relative_to(Path(sys.prefix))


def under_prefix(path: str) -> str:
    """`path` written relative to sys.prefix, which is the directory."""
    return Path(path).relative_to(Path(sys.prefix)).as_posix()


def main() -> int:
    # A virtual environment is exactly this: an interpreter whose prefix is
    # not the prefix it was built with. There is no registry entry, no
    # machine-wide setting and nothing a second process can see.
    print(f"prefix differs from base_prefix: {sys.prefix != sys.base_prefix}")
    print(f"the interpreter is inside it:    "
          f"{inside_environment(sys.executable)}")

    # An installed third-party package, imported the ordinary way. pydantic
    # is a dependency of this project; chapter 9 is where it does any work.
    import pydantic

    package = str(Path(pydantic.__file__).parent)
    print(f"pydantic is inside it:           "
          f"{inside_environment(package)}")
    print(f"  ...at:                         {under_prefix(package)}")

    # And one that is not: the standard library ships with the interpreter,
    # so it is not in site-packages and never appears in a lockfile.
    import json

    assert json.__file__ is not None
    print(f"the standard library is:         "
          f"{inside_environment(json.__file__)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
