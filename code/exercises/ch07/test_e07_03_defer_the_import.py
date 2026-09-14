import sys

from exercises._loader import load

KEY = "e07_03_defer_the_import"


def test_importing_costs_nothing_and_calling_pays() -> None:
    # Pop it first, so the answer is about this module rather than about
    # whatever else the test session happened to import.
    sys.modules.pop("colorsys", None)
    module = load("ch07", KEY)
    assert "colorsys" not in sys.modules, (
        "importing this module still imports colorsys; move the import "
        "inside to_hsv"
    )
    assert module.to_hsv("red") == (0.0, 1.0, 1.0)
    assert "colorsys" in sys.modules


def test_the_module_does_not_bind_colorsys_as_an_attribute() -> None:
    module = load("ch07", KEY)
    assert not hasattr(module, "colorsys"), (
        "a module-level import binds the name on the module; an import "
        "inside a function binds it in that function's locals"
    )
    hue, saturation, value = module.to_hsv("lime")
    assert (round(hue, 4), saturation, value) == (0.3333, 1.0, 1.0)
