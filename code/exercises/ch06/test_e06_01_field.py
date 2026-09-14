import pytest

from exercises._loader import load


def test_returns_the_field() -> None:
    module = load("ch06", "e06_01_field")
    assert module.field_of({"host": "db-1"}, "host") == "db-1"


def test_missing_field_raises_the_modules_own_error() -> None:
    module = load("ch06", "e06_01_field")
    with pytest.raises(module.MissingFieldError):
        module.field_of({"host": "db-1"}, "port")


def test_the_original_keyerror_is_the_cause() -> None:
    module = load("ch06", "e06_01_field")
    with pytest.raises(module.MissingFieldError) as caught:
        module.field_of({}, "port")
    assert isinstance(caught.value.__cause__, KeyError)
