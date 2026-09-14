"""Reference solution for exercise 12.4."""

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
        self.in_flight = max(0, self.in_flight - 1)

    def begin_shutdown(self) -> None:
        # Readiness only. Liveness stays true for the whole drain: the
        # process is not sick, it is leaving, and a failed liveness probe
        # would have it killed with requests still in flight.
        self.shutting_down = True
        self.ready = False

    @property
    def may_exit(self) -> bool:
        return self.shutting_down and self.in_flight == 0
