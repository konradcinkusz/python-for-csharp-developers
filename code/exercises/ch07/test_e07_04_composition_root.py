from datetime import date

from exercises._loader import load

KEY = "e07_04_composition_root"


class FixedClock:
    """A fake. It inherits from nothing and is registered nowhere."""

    def today(self) -> date:
        return date(2026, 9, 14)


class ListSink:
    def __init__(self) -> None:
        self.lines: list[str] = []

    def send(self, message: str) -> None:
        self.lines.append(message)


def test_build_returns_something_callable_with_one_argument() -> None:
    module = load("ch07", KEY)
    service = module.build(FixedClock(), ListSink())
    assert callable(service)


def test_the_wired_service_uses_what_the_root_gave_it() -> None:
    module = load("ch07", KEY)
    sink = ListSink()
    service = module.build(FixedClock(), sink)
    service("certificate")
    assert sink.lines == ["certificate checked on 2026-09-14"]


def test_two_roots_wire_two_independent_services() -> None:
    # Nothing is global, so a second wiring shares nothing with the first.
    # A container with a singleton lifetime would not give you this.
    module = load("ch07", KEY)
    first, second = ListSink(), ListSink()
    module.build(FixedClock(), first)("a")
    module.build(FixedClock(), second)("b")
    assert first.lines == ["a checked on 2026-09-14"]
    assert second.lines == ["b checked on 2026-09-14"]
