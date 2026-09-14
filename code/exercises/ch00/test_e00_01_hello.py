from exercises._loader import load


def test_greets_by_name() -> None:
    module = load("ch00", "e00_01_hello")
    assert module.greet("Ada") == "Hello, Ada. Open the next listing."


def test_greeting_is_a_str_not_bytes() -> None:
    module = load("ch00", "e00_01_hello")
    assert isinstance(module.greet("Ada"), str)
