"""Reference solution for exercise 1.2."""

import sys

RAN: list[str] = []


def main() -> int:
    """Record that the program ran, print one line, and return 0."""
    RAN.append("main")
    print("ran as a program")
    return 0


# __name__ is this module's own name when it was imported, and the string
# "__main__" when the interpreter was pointed at this file -- by path, or
# by `python -m`. Handing main()'s value to sys.exit() is what turns a
# return code into an exit code.
if __name__ == "__main__":
    sys.exit(main())
