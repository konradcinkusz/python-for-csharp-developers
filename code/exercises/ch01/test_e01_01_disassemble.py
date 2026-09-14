from exercises._loader import load


def constant() -> int:
    return 7


def arithmetic(a: float, b: float) -> float:
    return a * b


def test_a_function_compiles_to_bytecode_before_it_is_called() -> None:
    module = load("ch01", "e01_01_disassemble")
    # Annotated rather than inferred: load() hands back a ModuleType, so
    # everything reached through it is Any, and a strict checker calls what
    # comes out of iterating an Any "Unknown". Chapter 3 is about that.
    names: list[str] = module.instruction_names(constant)
    assert isinstance(names, list)
    assert all(isinstance(name, str) for name in names)
    assert names, "a function with a body compiles to at least one opcode"


def test_every_function_starts_at_resume_and_ends_by_returning() -> None:
    module = load("ch01", "e01_01_disassemble")
    for func in (constant, arithmetic):
        names: list[str] = module.instruction_names(func)
        assert names[0] == "RESUME"
        assert names[-1] == "RETURN_VALUE"


def test_the_arithmetic_is_one_opcode_not_a_method_call() -> None:
    module = load("ch01", "e01_01_disassemble")
    assert "BINARY_OP" in module.instruction_names(arithmetic)
    assert "BINARY_OP" not in module.instruction_names(constant)
