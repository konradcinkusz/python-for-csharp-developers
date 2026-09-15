"""The service experiment E5 drives: one awaited upstream, one CPU handler.

Not a listing: it is the subject of a measurement, and it lives under
measure/ so that uvicorn can be given `measure.e05_app:app` as an import
string. Workers above one REQUIRE an import string -- uvicorn logs "You
must pass the application as an import string to enable 'reload' or
'workers'." and exits with a startup failure when handed an app object,
which is checked in uvicorn.main.run at the pinned version.

Three routes, and each answers a different question:

  /noop    returns at once. It is the CALIBRATION endpoint: it measures
           the load driver and the loopback, not the service, and a cell
           whose throughput is anywhere near this one is a measurement of
           the client. The LangChain book's chapter 13 lost a run to
           exactly that and the guard is inherited from it.
  /await   awaits a fixed delay: the mocked upstream. One event loop can
           hold thousands of these at once because none of them is
           running.
  /cpu     burns a fixed number of bytecode operations. Nothing releases
           the GIL, so a second request on the same worker waits.
  /who     names the worker process that answered. Workers share one
           listening socket, so which of them serves a connection is
           settled once, at accept, and holds for the life of that
           connection -- and that is measurable rather than arguable.
"""

from __future__ import annotations

import asyncio
import os
from typing import Any

from fastapi import FastAPI

DELAY_SECONDS = float(os.environ.get("E05_DELAY_SECONDS", "0.1"))
BURN_ROUNDS = int(os.environ.get("E05_BURN_ROUNDS", "200000"))

app = FastAPI()


def burn(rounds: int) -> int:
    total = 0
    for i in range(rounds):
        total = (total * 31 + i) % 1000003
    return total


@app.get("/noop")
async def noop() -> dict[str, bool]:
    return {"ok": True}


@app.get("/await")
async def awaited() -> dict[str, bool]:
    await asyncio.sleep(DELAY_SECONDS)
    return {"ok": True}


@app.get("/cpu")
async def cpu() -> dict[str, int]:
    return {"total": burn(BURN_ROUNDS)}


@app.get("/who")
async def who() -> dict[str, Any]:
    return {"pid": os.getpid()}
