"""The query you did not write: reading an object after commit().

A Session expires every object it holds when you commit, so the next
attribute you touch is a SELECT. In a loop over rows you already had, that
is one SELECT per row, issued by a line that reads like a field access.

Run it from code/:

    uv run python ch10/expiry.py
"""

from __future__ import annotations

from counting import Selects
from model import Service, seeded_engine
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

# --8<-- [start:expired]


def rename_then_report(engine: Engine, expire: bool) -> tuple[int, int]:
    """Rename every service, commit, then read the names back."""
    with Session(engine, expire_on_commit=expire) as session:
        services = list(session.scalars(select(Service)))
        for service in services:
            service.name = service.name.upper()
        session.commit()
        with Selects(engine) as counted:
            # Nothing here looks like a query. Under the default this
            # line is one SELECT per object, because commit() expired
            # every one of them.
            _ = [service.name for service in services]
        session.rollback()
    return len(services), counted.count


# --8<-- [end:expired]


def main() -> int:
    engine = seeded_engine()
    rows, default = rename_then_report(engine, expire=True)
    _, kept = rename_then_report(engine, expire=False)
    print(f"{rows} objects, read after commit")
    print(f"  expire_on_commit=True  (the default): {default} SELECTs")
    print(f"  expire_on_commit=False:               {kept} SELECTs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
