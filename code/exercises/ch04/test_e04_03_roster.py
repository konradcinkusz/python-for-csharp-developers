import pytest

from exercises._loader import load


def _roster_class() -> type:
    return load("ch04", "e04_03_roster").Roster


def test_len_and_indexing() -> None:
    roster = _roster_class()(["Ada", "Grace", "Alan"])
    assert len(roster) == 3
    assert roster[1] == "Grace"


def test_iterating_yields_the_names_in_order() -> None:
    roster = _roster_class()(["Ada", "Grace", "Alan"])
    assert list(roster) == ["Ada", "Grace", "Alan"]
    assert sum(1 for _ in roster) == 3


def test_membership_ignores_case() -> None:
    roster = _roster_class()(["Ada", "Grace"])
    assert "ada" in roster
    assert "ADA" in roster
    assert "Ada" in roster
    assert "Babbage" not in roster


def test_first_is_a_property_not_a_method() -> None:
    roster = _roster_class()(["Ada", "Grace"])
    assert roster.first == "Ada"
    assert _roster_class()([]).first is None


def test_first_is_read_only() -> None:
    roster = _roster_class()(["Ada"])
    with pytest.raises(AttributeError):
        roster.first = "Grace"
