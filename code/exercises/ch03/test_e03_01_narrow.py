from collections.abc import Sequence
from typing import TypeIs, get_args, get_origin

from exercises._loader import load


def test_answers_correctly() -> None:
    module = load("ch03", "e03_01_narrow")
    assert module.is_str_list(["a", "b"]) is True
    assert module.is_str_list([]) is True
    assert module.is_str_list(["a", 1]) is False
    assert module.is_str_list([None]) is False


def test_narrows_rather_than_merely_answering() -> None:
    module = load("ch03", "e03_01_narrow")
    returns = module.is_str_list.__annotations__["return"]
    assert get_origin(returns) is TypeIs, (
        "annotate the return as TypeIs[...]: a bool is an answer, and "
        "only a TypeIs is an answer the checker can use"
    )
    assert get_args(returns) == (Sequence[str],)
