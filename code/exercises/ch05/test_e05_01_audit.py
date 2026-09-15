from collections.abc import Callable
from types import ModuleType

from exercises._loader import load


def _decorated() -> tuple[ModuleType, Callable[..., str]]:
    module = load("ch05", "e05_01_audit")
    module.CALLS.clear()

    @module.audit
    def widen(text: str, by: int = 1) -> str:
        """Pad text on both sides."""
        return " " * by + text + " " * by

    return module, widen


def test_the_wrapped_function_still_returns_what_it_did() -> None:
    _, widen = _decorated()
    assert widen("x") == " x "
    assert widen("x", by=2) == "  x  "


def test_every_call_is_recorded() -> None:
    module, widen = _decorated()
    widen("a")
    widen("b")
    assert module.CALLS == ["widen", "widen"]


def test_the_name_survives_the_decorator() -> None:
    _, widen = _decorated()
    assert widen.__name__ == "widen"


def test_the_docstring_survives_the_decorator() -> None:
    _, widen = _decorated()
    assert widen.__doc__ == "Pad text on both sides."
