"""What SIGTERM has to do before the process is allowed to die.

Run it from code/:

    uv run python ch12/shutdown.py

The sequence uvicorn runs on SIGTERM is, in order: stop accepting new
connections, ask the open ones to finish, wait for the in-flight tasks,
and only then run the lifespan's shutdown half. Read it in the installed
package -- uvicorn/server.py, `Server.shutdown` -- rather than taking it
from here.

What that sequence does NOT do is tell the load balancer. Between the
signal arriving and the balancer noticing, every request it still routes
here meets a closed socket. So the first thing the handler below does is
fail readiness, and the drain only starts afterwards; the gap is the
balancer's polling interval and you are meant to wait it out.

This one sends itself the signal so that it terminates. A real process
waits.
"""

import asyncio
import os
import signal
import sys
from dataclasses import dataclass


@dataclass
class Health:
    """Two questions, and they are not the same question."""

    live: bool = True  # restart me
    ready: bool = True  # send me traffic

    def say(self, what: str) -> None:
        print(f"{what:<34} live={self.live} ready={self.ready}")


async def in_flight(health: Health) -> None:
    """One request that was already running when the signal arrived."""
    await asyncio.sleep(0.05)
    health.say("request finished")


async def main() -> int:
    health = Health()
    stopping = asyncio.Event()
    loop = asyncio.get_running_loop()

    def on_sigterm() -> None:
        # Readiness first. Liveness stays true: the process is not sick,
        # it is leaving, and a failed liveness probe would get it killed
        # in the middle of the drain.
        health.ready = False
        health.say("SIGTERM: readiness withdrawn")
        stopping.set()

    loop.add_signal_handler(signal.SIGTERM, on_sigterm)

    health.say("serving")
    request = asyncio.create_task(in_flight(health))
    await asyncio.sleep(0.01)
    os.kill(os.getpid(), signal.SIGTERM)

    await stopping.wait()
    health.say("draining")
    await request
    health.say("lifespan shutdown runs now")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
