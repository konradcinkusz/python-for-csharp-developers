"""Why `logging.basicConfig` is not `ILogger` configuration.

Run it from code/:

    uv run python ch12/logging_default.py

There are two calls to basicConfig here and only the first one does
anything. The second is a complete no-op: no exception, no warning, no
return value to check. In a real service the first call is not yours at
all -- any library that logs at import time makes it for you, with no
arguments -- and by the time your own configuration runs there is already
a handler on the root logger, which is the one condition basicConfig
refuses to act under.

Everything below goes to stdout on purpose. The module's own default is
stderr, which is a second thing about it that is not what a container
wants.
"""

import logging
import sys


def levelname(logger: logging.Logger) -> str:
    """The effective level of `logger`, as the name people quote."""
    return logging.getLevelName(logger.getEffectiveLevel())


def main() -> int:
    root = logging.getLogger()
    print("handlers before anybody configures:", len(root.handlers))

    # Call one. This is the library's, not yours: `logging.warning(...)`
    # at import time calls basicConfig() internally with no arguments.
    logging.basicConfig(stream=sys.stdout)
    print("handlers after the first call:  ", len(root.handlers))
    print("level after the first call:     ", levelname(root))

    # Call two. This is yours, and it asks for a different level and a
    # different format. Read the next two lines before you decide what
    # they will say.
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.DEBUG,
        format="%(levelname)s|%(name)s|%(message)s",
    )
    print("level after the second call:    ", levelname(root))
    logging.getLogger("app").debug("the DEBUG line you asked for")
    logging.getLogger("app").warning("a WARNING line, in whose format?")

    # force=True is the standard library's own answer: drop every handler
    # that is already there and configure from scratch.
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.DEBUG,
        format="%(levelname)s|%(name)s|%(message)s",
        force=True,
    )
    print("level after force=True:         ", levelname(root))
    logging.getLogger("app").debug("and now the DEBUG line arrives")
    return 0


if __name__ == "__main__":
    sys.exit(main())
