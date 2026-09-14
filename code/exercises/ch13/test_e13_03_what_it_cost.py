from decimal import Decimal

from exercises._loader import load

IN_RATE = Decimal("300")     # pence per million input tokens
OUT_RATE = Decimal("1500")   # pence per million output tokens


def test_one_call_is_priced_exactly() -> None:
    module = load("ch13", "e13_03_what_it_cost")
    # 41 * 300 + 17 * 1500 = 12300 + 25500 = 37800, over a million.
    cost = module.call_cost(41, 17, IN_RATE, OUT_RATE)
    assert cost == Decimal("0.0378")


def test_output_is_dearer_than_input() -> None:
    module = load("ch13", "e13_03_what_it_cost")
    same = module.call_cost(1000, 0, IN_RATE, OUT_RATE)
    other = module.call_cost(0, 1000, IN_RATE, OUT_RATE)
    assert other > same


def test_a_free_call_costs_nothing() -> None:
    module = load("ch13", "e13_03_what_it_cost")
    assert module.call_cost(0, 0, IN_RATE, OUT_RATE) == Decimal("0")


def test_the_answer_is_a_decimal_not_a_float() -> None:
    module = load("ch13", "e13_03_what_it_cost")
    assert isinstance(module.call_cost(41, 17, IN_RATE, OUT_RATE), Decimal)


def test_a_thousand_calls_sum_without_drifting() -> None:
    module = load("ch13", "e13_03_what_it_cost")
    one = module.call_cost(41, 17, IN_RATE, OUT_RATE)
    assert sum([one] * 1000) == Decimal("37.8000")
