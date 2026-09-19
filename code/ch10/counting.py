"""The instrument the rest of the chapter is measured with.

The engine's echo prints every statement it runs, and counting those lines
is what a person does by eye. This counts them twice, from two places, and
refuses to report a number the two disagree about:

  * `before_cursor_execute`, the event the echo is emitted from, and
  * the echo itself, as log records on sqlalchemy.engine.Engine.

Two instruments agreeing is the only reason to believe either, and these
two watch the same statement from opposite ends: the hook sees it on its
way to the driver, the log sees the line a reader would have counted.

Note the level is raised and restored rather than assumed. An echo-counting
instrument on an engine whose logger is at WARNING counts nothing, agrees
with nothing, and reports a confident zero.

Run it from code/:

    uv run python ch10/counting.py
"""

from __future__ import annotations

import logging
from types import TracebackType
from typing import Any

from sqlalchemy import Engine, event
from sqlalchemy.orm import Session

ECHO_LOGGER = "sqlalchemy.engine.Engine"

# --8<-- [start:counter]


class _EchoLines(logging.Handler):
    """Counts the SELECT lines the engine's echo prints."""

    def __init__(self) -> None:
        super().__init__()
        self.selects = 0

    def emit(self, record: logging.LogRecord) -> None:
        if record.getMessage().lstrip().startswith("SELECT"):
            self.selects += 1


class Selects:
    """How many SELECTs did the block inside this `with` cost?"""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self.count = 0
        self._echo = _EchoLines()
        self._log = logging.getLogger(ECHO_LOGGER)
        self._level = self._log.level

    def _hook(self, _conn: Any, _cur: Any, statement: str, *_: Any) -> None:
        if statement.lstrip().startswith("SELECT"):
            self.count += 1

    def __enter__(self) -> Selects:
        event.listen(self.engine, "before_cursor_execute", self._hook)
        self._log.addHandler(self._echo)
        self._log.setLevel(logging.INFO)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        event.remove(self.engine, "before_cursor_execute", self._hook)
        self._log.removeHandler(self._echo)
        self._log.setLevel(self._level)
        if self.count != self._echo.selects:
            raise AssertionError(
                f"the hook counted {self.count} SELECTs and the echo "
                f"counted {self._echo.selects}; one of them is wrong"
            )


# --8<-- [end:counter]


def main() -> int:
    # The counter knows about an engine and nothing about this chapter's
    # model, so the model is imported by the demonstration rather than by
    # the module -- which is also what lets the exercises import Selects
    # without dragging ch10/model.py along behind it.
    from model import Service, seeded_engine
    from sqlalchemy import select

    engine = seeded_engine()
    with Selects(engine) as counted, Session(engine) as session:
        session.scalars(select(Service)).all()
    print(f"one query, counted from both ends: {counted.count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
