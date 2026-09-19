import pytest

from exercises._loader import load

GOOD = '{"host": "db.internal", "port": "8080"}'


def test_returns_a_typed_object() -> None:
    module = load("ch03", "e03_04_boundary")
    settings = module.parse_settings(GOOD)
    assert settings.host == "db.internal"
    assert settings.port == 8080
    # The point of the exercise: not merely equal to 8080, but an int.
    assert isinstance(settings.port, int)
    assert not isinstance(settings.port, str)


@pytest.mark.parametrize(
    "blob",
    [
        '{"host": "db.internal", "port": "eighty"}',
        '{"host": "db.internal"}',
        '{"port": 8080}',
        "not json at all",
    ],
)
def test_refuses_what_it_cannot_produce(blob: str) -> None:
    module = load("ch03", "e03_04_boundary")
    with pytest.raises(ValueError):
        module.parse_settings(blob)
