from exercises._loader import load

KEY = "e07_02_public_surface"


def star_import(module: object) -> set[str]:
    """The names `from module import *` would copy, without doing it."""
    declared = getattr(module, "__all__", None)
    if declared is not None:
        return set(declared)
    return {n for n in vars(module) if not n.startswith("_")}


def test_the_module_declares_what_it_exports() -> None:
    module = load("ch07", KEY)
    assert hasattr(module, "__all__"), (
        "without __all__ a star import copies every public name, including "
        "the modules this one imported"
    )


def test_star_copies_two_names_and_the_helpers_are_still_reachable(
) -> None:
    module = load("ch07", KEY)
    assert star_import(module) == {"net_total", "format_money"}
    # __all__ governs the star import and hides nothing: a caller that asks
    # for a helper by name still gets it, which is the difference between a
    # convention and C#'s `internal`.
    assert callable(module.round_pennies)
    assert callable(module.add_vat)
