"""Exercise 12.4 -- the order the shutdown has to happen in.

Two probes, and an orchestrator treats them completely differently:
liveness failing gets the process killed and replaced, readiness failing
gets it taken out of the load balancer and left alone. Confusing them
during a shutdown is how a rolling deploy drops requests.

Finish the three methods so that:

  * a fresh instance is both live and ready;
  * `begin_shutdown` withdraws readiness and LEAVES liveness alone -- a
    draining process is not a sick one, and failing liveness here gets it
    killed in the middle of the drain;
  * `finish_request` decrements the in-flight count, and `may_exit` is
    true only once the shutdown has begun and nothing is in flight.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Lifecycle:
    """What the two probes answer, and when the process may leave."""

    live: bool = True
    ready: bool = True
    in_flight: int = 0
    shutting_down: bool = False

    def begin_request(self) -> None:
        self.in_flight += 1

    def finish_request(self) -> None:
        raise NotImplementedError("your turn: replace this line")

    def begin_shutdown(self) -> None:
        raise NotImplementedError("your turn: replace this line")

    @property
    def may_exit(self) -> bool:
        raise NotImplementedError("your turn: replace this line")
