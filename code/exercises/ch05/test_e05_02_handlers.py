from types import ModuleType

from exercises._loader import load


def _module() -> ModuleType:
    return load("ch05", "e05_02_handlers")


def test_broken_is_still_broken() -> None:
    module = _module()
    # Not a mistake: the trap has to keep working, or the fix proves
    # nothing. Every closure sees the variable's last value.
    assert [fn() for fn in module.broken(3)] == [2, 2, 2]
    assert [fn() for fn in module.fixed_by_default(3)] == [0, 1, 2]


def test_default_argument_binds_at_definition() -> None:
    module = _module()
    assert [fn() for fn in module.fixed_by_default(4)] == [0, 1, 2, 3]


def test_partial_binds_when_partial_runs() -> None:
    module = _module()
    assert [fn() for fn in module.fixed_by_partial(4)] == [0, 1, 2, 3]


def test_each_function_is_independent() -> None:
    module = _module()
    handlers = module.fixed_by_partial(3)
    assert handlers[0]() == 0
    assert handlers[2]() == 2
    assert handlers[0]() == 0
