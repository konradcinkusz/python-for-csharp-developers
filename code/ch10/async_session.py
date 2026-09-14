"""The async session, and the one place it is not the sync one with awaits.

Almost everything transfers: the same model, the same select(), the same
unit of work, with `await` in front of the calls that touch the database.
What does not transfer is lazy loading. Under the async session a lazy
relationship does not quietly issue a query -- it raises, because issuing
one there would mean blocking the event loop, and nothing is allowed to.

Run it from code/:

    uv run python ch10/async_session.py
"""

from __future__ import annotations

import asyncio

from model import Base, Incident, Service
from sqlalchemy import select
from sqlalchemy.exc import MissingGreenlet
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import selectinload

Factory = async_sessionmaker[AsyncSession]

# --8<-- [start:engine]


def make_factory(engine: AsyncEngine) -> Factory:
    """expire_on_commit=False is not a tuning knob under async.

    An expired attribute reloads itself on next access, and under the
    async session that reload is the error below rather than a query --
    so leaving the default on would arm a landmine at every commit.
    """
    return async_sessionmaker(engine, expire_on_commit=False)


# --8<-- [end:engine]

# --8<-- [start:lazy]


async def lazy_under_async(factory: Factory) -> str:
    """The loop that silently N+1s in a sync service, run asynchronously."""
    async with factory() as session:
        service = (await session.scalars(select(Service))).first()
        assert service is not None
        try:
            return f"loaded {len(service.incidents)} incidents"
        except MissingGreenlet:
            return "MissingGreenlet"


async def eager_under_async(factory: Factory) -> dict[str, int]:
    """Say what you want up front and the async session is unremarkable."""
    async with factory() as session:
        statement = select(Service).options(selectinload(Service.incidents))
        return {
            service.name: sum(i.minutes for i in service.incidents)
            for service in (await session.scalars(statement)).unique()
        }


# --8<-- [end:lazy]


async def seeded() -> AsyncEngine:
    engine = create_async_engine("sqlite+aiosqlite://")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    async with make_factory(engine)() as session:
        api = Service(name="api")
        api.incidents = [Incident(title="t", severity=1, minutes=42)]
        session.add(api)
        await session.commit()
    return engine


async def main() -> int:
    engine = await seeded()
    factory = make_factory(engine)
    print(f"lazy:  {await lazy_under_async(factory)}")
    print(f"eager: {await eager_under_async(factory)}")
    await engine.dispose()
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
