from typing import Any

from exercises._loader import load


def _basket_class() -> Any:
    """The exercise's Basket, widened once, here.

    The other three tests in this chapter annotate `-> type`, which is
    enough while they only construct the class. This one reads a class
    ATTRIBUTE off it, and `type` says nothing about what attributes a
    class has -- so pyright strict reports `opened` as unknown, correctly.
    Chapter 3's rule is the one that applies: widen at the boundary, in
    one documented place, rather than relax the checker for a directory.
    """
    module = load("ch04", "e04_04_shared")
    module.Basket.opened = 0
    return module.Basket


def test_two_baskets_do_not_share_their_items() -> None:
    basket = _basket_class()
    mine, yours = basket(), basket()
    mine.add("apple", 60)
    yours.add("pear", 80)
    assert [name for name, _ in mine.items] == ["apple"]
    assert [name for name, _ in yours.items] == ["pear"]
    assert mine.items is not yours.items


def test_chained_adds_land_in_that_basket_only() -> None:
    """Chaining AND isolation in one assertion, deliberately.

    `add` already returns self on the starter, so a test that checked only
    the chaining would pass before the reader had done anything -- which
    the strict-xfail gate reports as a failure, and rightly: a test that
    does not depend on the answer is not a check.
    """
    basket = _basket_class()
    basket().add("apple", 60)
    yours = basket().add("pear", 80).add("plum", 30)
    assert [name for name, _ in yours.items] == ["pear", "plum"]


def test_total_is_a_property() -> None:
    basket = _basket_class()
    mine = basket().add("apple", 60).add("pear", 80)
    assert mine.total == 140


def test_opened_counts_on_the_class_and_is_shared_on_purpose() -> None:
    basket = _basket_class()
    first, second = basket(), basket()
    assert basket.opened == 2
    assert first.opened == 2
    assert second.opened == 2
