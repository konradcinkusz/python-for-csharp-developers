from exercises._loader import load


def _seat_class() -> type:
    return load("ch04", "e04_01_hashable").Seat


def test_seats_with_the_same_row_and_number_are_equal() -> None:
    seat = _seat_class()
    assert seat("A", 12) == seat("A", 12)


def test_a_different_seat_is_not_equal() -> None:
    seat = _seat_class()
    assert seat("A", 12) != seat("A", 13)
    assert seat("A", 12) != seat("B", 12)


def test_comparing_with_another_type_is_not_an_error() -> None:
    seat = _seat_class()
    assert seat("A", 12) != "A12"


def test_a_seat_is_still_usable_as_a_dict_key() -> None:
    seat = _seat_class()
    booked = {seat("A", 12): "taken"}
    assert booked[seat("A", 12)] == "taken"


def test_equal_seats_hash_equal_so_a_set_holds_one() -> None:
    seat = _seat_class()
    assert len({seat("A", 12), seat("A", 12)}) == 1
